from rest_framework.views import APIView
from rest_framework import status

from seahub import settings
from seahub.settings import DOI_SERVER, DOI_USER, DOI_PASSWORD, DOI_TIMEOUT, BLOXBERG_SERVER, SERVICE_URL
from seahub.base.templatetags.seahub_tags import email2nickname, email2contact_email
from seahub.api2.utils import json_response
from seahub.share.models import FileShare
from seahub.utils import gen_shared_link
from seaserv import seafile_api

from keeper.catalog.catalog_manager import get_catalog
from keeper.bloxberg.bloxberg_manager import hash_file, create_bloxberg_certificate
from keeper.doi.doi_manager import get_metadata, generate_metadata_xml, get_latest_commit_id, send_notification
from keeper.models import CDC, DoiRepo, ArchiveQuota, ArchiveRepo

from django.http import JsonResponse
from django.shortcuts import render

from django.utils.translation import ugettext as _


import logging
import datetime
import requests
from requests.exceptions import ConnectionError, Timeout
from keeper.utils import add_keeper_archiving_task

logger = logging.getLogger(__name__)

BLOXBERG_URL = BLOXBERG_SERVER + "/certifyData"
DOXI_URL = DOI_SERVER + "/doxi/rest/doi"


def is_in_mpg_ip_range(ip):
    # https://gwdu64.gwdg.de/pls/mpginfo/ip.liste2?version=edoc&aclgroup=mpg-allgemein
    return True

class CatalogView(APIView):
    """
    Returns Keeper Catalog.
    """
    @json_response
    def get(self, request, format=None):
        catalog = get_catalog()
        return catalog

def certify_file(request):
    repo_id = request.GET.get('repo_id', None)
    path = request.GET.get('path', None)
    user_email = request.user.username
    hash_data = hash_file(repo_id, path, user_email)
    response_bloxberg = request_bloxberg(hash_data)

    if response_bloxberg is not None:
        if response_bloxberg.status_code == 200:
            transaction_id = response_bloxberg.json()['txReceipt']['transactionHash']
            checksum = hash_data['certifyVariables']['checksum']
            created_time = datetime.datetime.fromtimestamp(float(hash_data['certifyVariables']['timestampString']))
            create_bloxberg_certificate(repo_id, path, transaction_id, created_time, checksum, user_email)
            return JsonResponse(response_bloxberg.json())

    return JsonResponse({'msg': 'Transaction failed'})

def request_bloxberg(certify_payload):
    try:
        response = requests.post(BLOXBERG_URL, json=certify_payload)
        return response
    except ConnectionError as e:
        logger.error(str(e))

def request_doxi(shared_link, doxi_payload):
    try:
        # credentials for https://test.doi.mpdl.mpg.de/
        user=DOI_USER
        pwd=DOI_PASSWORD
        headers = {'Content-Type': 'text/xml'}
        response = requests.put(DOXI_URL, auth=(user, pwd), headers=headers, params={'url': shared_link}, data=doxi_payload, timeout=DOI_TIMEOUT)
        return response
    except Timeout:
        return JsonResponse({
            'msg': 'DOXI request timeout',
            'status': 'error',
            }, status=408)
    except ConnectionError as e:
        logger.error(str(e))

def get_landing_page_url(repo_id, commit_id):
    return "{}/doi/libs/{}/{}".format(SERVICE_URL, repo_id, commit_id)

def add_doi(request):
    repo_id = request.GET.get('repo_id', None)
    user_email = request.user.username
    repo = get_repo(repo_id)
    doi_repos = DoiRepo.objects.get_valid_doi_repos(repo_id)
    if doi_repos:
        msg = 'This library already has a DOI. '
        url_landing_page = get_landing_page_url(doi_repos[0].repo_id, doi_repos[0].commit_id)
        send_notification(msg, repo_id, 'error', user_email, doi_repos[0].doi, url_landing_page)
        return JsonResponse({
            'msg': msg + doi_repos[0].doi,
            'status': 'error',
            })

    metadata = get_metadata(repo_id, user_email, "doi")

    if 'error' in metadata:
        return JsonResponse({
            'msg': metadata.get('error'),
            'status': 'error',
            })

    metadata_xml = generate_metadata_xml(metadata)
    commit_id = get_latest_commit_id(repo)

    url_landing_page = get_landing_page_url(repo_id, commit_id)
    response_doxi = request_doxi(url_landing_page, metadata_xml)

    if response_doxi is not None:
        if response_doxi.status_code == 201:
            doi = 'https://doi.org/' + response_doxi.text
            logger.info(doi)
            repo_owner = get_repo_owner(repo_id)
            DoiRepo.objects.add_doi_repo(repo_id, repo.name, doi, None, commit_id, repo_owner, metadata)
            msg = _(u'DOI successfully created') + ': '
            doi_repos = DoiRepo.objects.get_doi_by_commit_id(repo_id, commit_id)
            send_notification(msg, repo_id, 'success', user_email, doi, url_landing_page, timestamp=doi_repos[0].created)
            return JsonResponse({
                'msg': msg + doi,
                'status': 'success',
                })
        elif response_doxi.status_code == 408:
            msg = 'The assign DOI functionality is currently unavailable. Please try again later. If the problem persists, please contact Keeper support.'
            send_notification(msg, repo_id, 'error', user_email)
            return JsonResponse({
                'msg': msg,
                'status': 'error'
            })
        else:
            logger.info(response_doxi.status_code)
            logger.info(response_doxi.text)
            msg = 'Failed to create DOI, ' + response_doxi.text
            send_notification(msg, repo_id, 'error', user_email)
            return JsonResponse({
                'msg': msg,
                'status': 'error'
                })
    else:
        msg = 'The assign DOI functionality is currently unavailable. Please try again later. If the problem persists, please contact Keeper support.'
        send_notification(msg, repo_id, 'error', user_email)
        return JsonResponse({
            'msg': msg,
            'status': 'error'
        })

def DoiView(request, repo_id, commit_id):
    doi_repos = DoiRepo.objects.get_doi_by_commit_id(repo_id, commit_id)
    repo_owner = get_repo_owner(repo_id)

    if len(doi_repos) == 0:
        return render(request, '404.html')
    elif len(doi_repos) > 0 and doi_repos[0].rm is not None:
        return render(request, './catalog_detail/tombstone_page.html', {
            'doi': doi_repos[0].doi,
            'md_dict': doi_repos[0].md,
            'authors': '; '.join(get_authors_from_md(doi_repos[0].md)),
            'institute': doi_repos[0].md.get("Institute").replace(";", "; "),
            'library_name': doi_repos[0].repo_name,
            'owner_contact_email': email2contact_email(repo_owner) })

    cdc = False if get_cdc_id_by_repo(repo_id) is None else True
    link = SERVICE_URL + "/repo/history/view/" + repo_id + "/?commit_id=" + commit_id

    return render(request, './catalog_detail/landing_page.html', {
        'share_link': link,
        'cdc': cdc,
        'authors': '; '.join(get_authors_from_md(doi_repos[0].md)),
        'institute': doi_repos[0].md.get("Institute").replace(";", "; "),
        'commit_id': commit_id,
        'doi_dict': doi_repos[0].md,
        'doi': doi_repos[0].doi,
        'owner_contact_email': email2contact_email(repo_owner) })

def get_authors_from_md(md):
    authors = md.get("Author").split('\n')
    result_author = []
    for author in authors:
        author_array = author.split(";")
        author_name = author_array[0].strip()
        name_array = author_name.split(", ")
        tmpauthor = ''
        for i in xrange(len(name_array)):
            if ( i <= 0 and len(name_array[i].strip()) > 1 ):
                tmpauthor += name_array[i]+", "
            elif (len(name_array[i].strip()) >= 1):
                tmpauthor += name_array[i].strip()[:1] + "."

        if len(author_array) > 1 and len(author_array[1].strip()) > 0:
            affiliations = author_array[1].split("|")
            tmpauthor += " (" + ", ".join(map(str.strip, affiliations)) + ")"

        result_author.append(tmpauthor)
    return result_author


def get_repo(repo_id):
    return seafile_api.get_repo(repo_id)

def get_repo_owner(repo_id):
    return seafile_api.get_repo_owner(repo_id)

def get_cdc_id_by_repo(repo_id):
    """Get cdc_id by repo_id. Return None if nothing found"""
    return CDC.objects.get_cdc_id_by_repo(repo_id)

def LandingPageView(request, repo_id):
    repo_owner = get_repo_owner(repo_id)
    if repo_owner is None:
        repo_owner_email = "keeper@mpdl.mpg.de"   # in case repo has no owner (Z.B deleted)
    else:
        repo_owner_email = email2contact_email(repo_owner)

    doi_repos = DoiRepo.objects.get_doi_repos_by_repo_id(repo_id)

    archive_repos = ArchiveRepo.objects.get_archive_repos_by_repo_id(repo_id)

    cdc = False if get_cdc_id_by_repo(repo_id) is None else True

    if doi_repos:
        md = doi_repos[0].md
    elif archive_repos:
        md = archive_repos[0].md
    
    if md:
        return render(request, './catalog_detail/lib_detail_landing_page.html', {
            'authors': '; '.join(get_authors_from_md(md)),
            'institute': md.get("Institute").replace(";", "; "),
            'doi_dict': md,
            'doi_repos': doi_repos,
            'archive_repos': archive_repos,
            'cdc': cdc,
            'owner_contact_email':  repo_owner_email
        })
    
    return render(request, '404.html')

def ArchiveView(request, repo_id, version_id):
    archive_repo = ArchiveRepo.objects.get_archive_repo_by_repo_id_and_version(repo_id, version_id)
    if archive_repo == None:
        return render(request, '404.html')

    repo_owner = get_repo_owner(repo_id)
    if repo_owner is None:
        repo_owner_email = "keeper@mpdl.mpg.de"   # in case repo has no owner (Z.B deleted)
        return render(request, './catalog_detail/tombstone_page.html', {
            'md_dict': archive_repo.md,
            'authors': '; '.join(get_authors_from_md(archive_repo.md)),
            'institute': archive_repo.md.get("Institute").replace(";", "; "),
            'library_name': archive_repo.repo_name,
            'owner_contact_email': email2contact_email(repo_owner) })
    else:
        repo_owner_email = email2contact_email(repo_owner)

    cdc = False if get_cdc_id_by_repo(repo_id) is None else True
    commit_id = archive_repo.commit_id
    link = SERVICE_URL + "/repo/history/view/" + repo_id + "/?commit_id=" + commit_id

    return render(request, './catalog_detail/archive_page.html', {
        'share_link': link,
        'authors': '; '.join(get_authors_from_md(archive_repo.md)),
        'institute': archive_repo.md.get("Institute").replace(";", "; "),
        'commit_id': commit_id,
        'md_dict': archive_repo.md,
        'cdc': cdc,
        'owner_contact_email': email2contact_email(repo_owner) })

def can_archive(request):

    repo_id = request.GET.get('repo_id', None)
    user_email = request.user.username
    repo = get_repo(repo_id)
    is_oversized = repo.size > 67108864000000000

    if is_oversized:
        return JsonResponse({
            'msg': "oversized",
            'status': "error"
        })
    
    quota = update_quota(repo_id, user_email)

    if quota <= 0: 
        return JsonResponse({
            'msg': "quota_expired",
            'status': "error"
        })
    else:
        return JsonResponse({
        'quota': quota,
        'status': "success"
    }) 

def archive_lib(request):

    """ archive library, double check quota to avoid misuse """
    repo_id = request.GET.get('repo_id', None)
    user_email = request.user.username
    repo = get_repo(repo_id)
    metadata = get_metadata(repo_id, user_email, "archive")

    if 'error' in metadata:
        return JsonResponse({
            'msg': metadata.get('error'),
            'status': 'error',
        })
    logger.info("Successfully get metadata, start archiving...")

    commit_id = get_latest_commit_id(repo)
    checksum = "todo:ask_vlad_how_to_get_checksum_of_zip"
    status = "in_process"
    external_path = "some_external_path"
    repo_name = repo.name

    resp1 = add_keeper_archiving_task(repo_id, user_email)
    logger.debug(resp1.__dict__)

    #archiveRepo = archive_finished(repo_id, repo_name, commit_id, user_email, checksum, external_path, metadata, status)

    #todo: set archive quota should be removed
    quota = ArchiveQuota.objects.set_archive_quota(repo_id, user_email)

    if quota == -1:
        msg = "Can not archive for this Library, please contact support"
    else:
        msg = "Archive started: " + resp1["status"]

    return JsonResponse({
            'msg': msg,
            'status': 'success'
        })

def archive_finished(repo_id, repo_name, commit_id, user_email, checksum, external_path, metadata, status):
    archiveRepo = ArchiveRepo.objects.create_archive_repo(repo_id, repo_name, commit_id, user_email, checksum, external_path, metadata, status)
    return archiveRepo

def update_quota(repo_id, owner):
    quota = ArchiveQuota.objects.get_archive_quota(repo_id, owner)

    if quota is None:
        quota = ArchiveQuota.objects.init_archive_quota(repo_id, owner)

    return quota.quota