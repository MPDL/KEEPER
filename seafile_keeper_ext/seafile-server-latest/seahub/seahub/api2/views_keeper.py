from rest_framework.views import APIView
from rest_framework import status

from seahub import settings
from seahub.auth.decorators import login_required
from seahub.base.decorators import user_mods_check
from seahub.settings import DOI_SERVER, DOI_USER, DOI_PASSWORD, DOI_TIMEOUT, BLOXBERG_SERVER, SERVICE_URL, SERVER_EMAIL
from seahub.base.templatetags.seahub_tags import email2nickname, email2contact_email
from seahub.api2.utils import json_response
from seahub.share.models import FileShare
from seahub.utils import gen_shared_link
from seaserv import seafile_api

from keeper.catalog.catalog_manager import get_catalog
from keeper.bloxberg.bloxberg_manager import hash_file, create_bloxberg_certificate
from keeper.doi.doi_manager import get_metadata, generate_metadata_xml, get_latest_commit_id, send_notification, MSG_TYPE_KEEPER_DOI_MSG, MSG_TYPE_KEEPER_DOI_SUC_MSG
from keeper.models import CDC, DoiRepo, Catalog

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from django.utils.translation import ugettext as _


import logging
import datetime
import requests
from requests.exceptions import ConnectionError, Timeout
from keeper.utils import add_keeper_archiving_task, query_keeper_archiving_status, check_keeper_repo_archiving_status
from keeper.common import parse_markdown_doi
from seafevents.keeper_archiving.db_oper import DBOper, MSG_TYPE_KEEPER_ARCHIVING_MSG
from seafevents.keeper_archiving.task_manager import MSG_DB_ERROR, MSG_ADD_TASK, MSG_WRONG_OWNER, MSG_MAX_NUMBER_ARCHIVES_REACHED, MSG_CANNOT_GET_QUOTA, MSG_LIBRARY_TOO_BIG, MSG_EXTRACT_REPO, MSG_ADD_MD, MSG_CREATE_TAR, MSG_PUSH_TO_HPSS, MSG_ARCHIVING_SUCCESSFUL, MSG_CANNOT_FIND_ARCHIVE, MSG_SNAPSHOT_ALREADY_ARCHIVED

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
        send_notification(msg, repo_id, MSG_TYPE_KEEPER_DOI_MSG, user_email, doi_repos[0].doi, url_landing_page)
        return JsonResponse({
            'msg': msg + doi_repos[0].doi,
            'status': 'error',
            })

    metadata = get_metadata(repo_id, user_email, "assign DOI")

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
            send_notification(msg, repo_id, MSG_TYPE_KEEPER_DOI_SUC_MSG, user_email, doi, url_landing_page, timestamp=doi_repos[0].created)
            return JsonResponse({
                'msg': msg + doi,
                'status': 'success',
                })
        elif response_doxi.status_code == 408:
            msg = 'The assign DOI functionality is currently unavailable. Please try again later. If the problem persists, please contact Keeper support.'
            send_notification(msg, repo_id, MSG_TYPE_KEEPER_DOI_MSG, user_email)
            return JsonResponse({
                'msg': msg,
                'status': 'error'
            })
        else:
            logger.info(response_doxi.status_code)
            logger.info(response_doxi.text)
            msg = 'Failed to create DOI, ' + response_doxi.text
            send_notification(msg, repo_id, MSG_TYPE_KEEPER_DOI_MSG, user_email)
            return JsonResponse({
                'msg': msg,
                'status': 'error'
                })
    else:
        msg = 'The assign DOI functionality is currently unavailable. Please try again later. If the problem persists, please contact Keeper support.'
        send_notification(msg, repo_id, MSG_TYPE_KEEPER_DOI_MSG, user_email)
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


@login_required
def LandingPageView(request, repo_id):

    repo_owner = get_repo_owner(repo_id)
    repo_contact_email = SERVER_EMAIL if repo_owner is None else request.user.username

    doi_repos = DoiRepo.objects.get_doi_repos_by_repo_id(repo_id)

    archive_repos = DBOper().get_archives(repo_id=repo_id)
    if archive_repos is not None and len(archive_repos) == 0:
        archive_repos = None

    catalog = Catalog.objects.get_by_repo_id(repo_id)
    md = catalog.md

    return render(request, './catalog_detail/lib_detail_landing_page.html', {
        'authors': get_authors_from_catalog_md(md),
        'md': md,
        'doi_repos': doi_repos,
        'archive_repos': archive_repos,
        'hasCDC': get_cdc_id_by_repo(repo_id) is not None,
        'owner_contact_email':  repo_contact_email
    })

def get_authors_from_catalog_md(md):
    result_authors = []
    for author in md.get("authors"):
        name_array = author.get("name").split(", ")
        tmp = name_array[0]
        if name_array[1]:
            tmp += ', ' + name_array[1][:1] + '.'
        affs = author.get("affs")
        if affs:
            tmp += " (" + ", ".join(map(unicode.strip, affs)) + ")"
        result_authors.append(tmp)

    return "; ".join(result_authors)



def ArchiveView(request, repo_id, version_id):
    archive_repos = DBOper().get_archives(repo_id=repo_id, version = version_id)
    if archive_repos is None or len(archive_repos) == 0:
        return render(request, '404.html')

    archive_repo = archive_repos[0]
    repo_owner = get_repo_owner(repo_id)
    archive_md = parse_markdown_doi((archive_repo.md).encode("utf-8"))
    if repo_owner is None:
        repo_owner_email = SERVER_EMAIL
        return render(request, './catalog_detail/tombstone_page.html', {
            'md_dict': archive_md,
            'authors': '; '.join(get_authors_from_md(archive_md)),
            'institute': archive_md.get("Institute").replace(";", "; "),
            'library_name': archive_repo.repo_name,
            'owner_contact_email': email2contact_email(repo_owner) })
    else:
        repo_owner_email = email2contact_email(repo_owner)

    cdc = False if get_cdc_id_by_repo(repo_id) is None else True
    commit_id = archive_repo.commit_id
    link = SERVICE_URL + "/repo/history/view/" + repo_id + "/?commit_id=" + commit_id

    return render(request, './catalog_detail/archive_page.html', {
        'share_link': link,
        'authors': '; '.join(get_authors_from_md(archive_md)),
        'institute': archive_md.get("Institute").replace(";", "; "),
        'commit_id': commit_id,
        'md_dict': archive_md,
        'cdc': cdc,
        'owner_contact_email': email2contact_email(repo_owner) })


class CanArchive(APIView):

    "Quota checking before adding archiving"
    def __init__(self):
        self.db_oper = DBOper()

    def get(self, request):
        repo_id = request.GET.get('repo_id', None)
        user_email = request.user.username
        repo = get_repo(repo_id)

        # library is already in the task query
        resp_query = query_keeper_archiving_status(repo_id, None)
        if resp_query.status in ('QUEUED', 'PROCESSING'):
            msg = "Library is already in archiving task queue, status: " + resp_query.status
            return JsonResponse({
                'msg': msg,
                'status': 'in_processing'
            })

        metadata = get_metadata(repo_id, user_email, "archive library")
        if 'error' in metadata:
            return JsonResponse({
                'msg': metadata.get('error'),
                'status': 'metadata_error',
            })

        resp_quota = check_keeper_repo_archiving_status(repo_id, user_email, 'get_quota')
        if resp_quota.remains <= 0:
            return JsonResponse({
                'status': "quota_expired"
            })

        resp_is_archived = check_keeper_repo_archiving_status(repo_id, user_email, 'is_snapshot_archived')
        if resp_is_archived.is_snapshot_archived == 'true':
            return JsonResponse({
                'status': "snapshot_archived"
            })

        resp_is_repo_too_big = check_keeper_repo_archiving_status(repo_id, user_email, 'is_repo_too_big')
        if resp_is_repo_too_big.is_repo_too_big == 'true':
            return JsonResponse({
                'status': "is_too_big"
            })



        return JsonResponse({
            'quota': resp_quota.remains,
            'status': "success"
        })


@require_POST
@json_response
def internal_add_keeper_archiving_task(requets):
    try:
        repo_id = request.POST.get('repo_id')
        owner = request.POST.get('owner')
    except KeyError:
        return HttpResponseBadRequest('invalid params')
    #TODO: check repo_id
    resp = vars(add_keeper_archiving_task(repo_id, owner))
    return resp['_dict']

@json_response
def internal_query_keeper_archiving_task(requets, repo_id, version):
    resp = vars(query_keeper_archiving_status(repo_id, version))
    return resp['_dict']

class ArchiveLib(APIView):

    """ create keeper archive for a library """
    def __init__(self):
        self.db_oper = DBOper()
        self.msg_dict = {
            MSG_DB_ERROR: 'There is a little problem with the server, please try later.',
            MSG_ADD_TASK: 'Cannot start archiving, please try later.',
            MSG_WRONG_OWNER: 'Only the owner can start archiving, please contact the library owner.',
            MSG_MAX_NUMBER_ARCHIVES_REACHED: 'Please contact support if you want to have more archives',
            MSG_CANNOT_GET_QUOTA: 'Cannot find archive quota for this library.',
            MSG_LIBRARY_TOO_BIG: '"Archive is only available for Libraries under 500G.',
            MSG_EXTRACT_REPO: 'Cannot extract current library, please contact support',
            MSG_ADD_MD: 'Cannot attack metadata file to library archive, please contact support.',
            MSG_CREATE_TAR: 'Cannot create tar file for archive, please contact support.',
            MSG_PUSH_TO_HPSS: 'Cannot push archive to HPSS, please contact support.',
            MSG_ARCHIVING_SUCCESSFUL: 'Library is successfully archived.',
            MSG_CANNOT_FIND_ARCHIVE: MSG_CANNOT_FIND_ARCHIVE,
            MSG_SNAPSHOT_ALREADY_ARCHIVED: MSG_SNAPSHOT_ALREADY_ARCHIVED,
        }

    def get(self, request):
        repo_id = request.GET.get('repo_id', None)
        user_email = request.user.username


        # add new archiving task
        resp_archive = add_keeper_archiving_task(repo_id, user_email)
        if resp_archive.status == 'ERROR':
            msg = self.msg_dict[resp_archive.error]
            send_notification(msg, repo_id, MSG_TYPE_KEEPER_ARCHIVING_MSG, user_email)
            return JsonResponse({
                'msg': msg,
                'status': 'error'
            })

        # status for "QUEUED" and "DONE"
        # TODO: add notification here if it is needed
        msg = "Archive for current library is " + resp_archive.status
        return JsonResponse({
                'msg': msg,
                'status': 'success'
            })
