from rest_framework.views import APIView
from rest_framework import status

from seahub import settings
from seahub.base.templatetags.seahub_tags import email2nickname, email2contact_email
from seahub.api2.utils import json_response
from seahub.share.models import FileShare
from seahub.utils import gen_shared_link
from seaserv import seafile_api

from keeper.catalog.catalog_manager import get_catalog
from keeper.bloxberg.bloxberg_manager import hash_file, create_bloxberg_certificate
from keeper.doi.doi_manager import get_metadata, generate_metadata_xml, get_lastest_commit_id
from keeper.models import CDC, DoiRepo

from django.http import JsonResponse
from django.shortcuts import render

import logging
import datetime
import requests
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)

URL = "https://bloxberg.org/certifyData"
DOXI_URL = "https://test.doi.mpdl.mpg.de/doxi/rest/doi"

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
        response = requests.post(URL, json=certify_payload)
        return response
    except ConnectionError as e:
        logger.error(str(e))

def request_doxi(shared_link, doxi_payload):
    try:
        # credentials for https://test.doi.mpdl.mpg.de/
        user=''
        pwd=''
        headers = {'Content-Type': 'text/xml'}
        response = requests.put(DOXI_URL, auth=(user, pwd), headers=headers, params={'url': shared_link}, data=doxi_payload)
        return response
    except ConnectionError as e:
        logger.error(str(e))

def add_doi(request):
    repo_id = request.GET.get('repo_id', None)
    host = request.GET.get('host', None)
    user_email = request.user.username
    metadata = get_metadata(repo_id, user_email)
    if metadata is None:
        return JsonResponse({'msg': 'metaData not valid'})
    metadata_xml = generate_metadata_xml(metadata)
    repo = get_repo(repo_id)
    commit_id = get_lastest_commit_id(repo)

    url_landing_page = host + '/doi/libs/' + repo_id + '&' + commit_id
    response_doxi = request_doxi(url_landing_page, metadata_xml)

    if response_doxi is not None:
        if response_doxi.status_code == 201:
            doi = response_doxi.text
            logger.info(doi)
            #todo: add to doi
            repo_owner = get_repo_owner(repo_id)
            DoiRepo.objects.add_doi_repo(repo_id, repo.name, 'https://doi.org/' + doi, None, commit_id, repo_owner, metadata)
            return JsonResponse({'msg': 'Create DOI successful: ' + 'https://doi.org/' + doi})
        else:
            logger.info(response_doxi.status_code)
            logger.info(response_doxi.text)
            return JsonResponse({'msg': 'Failed to create DOI, ' + response_doxi.text})
        
def DoiView(request, repo_id, commit_id):
    doi_repos = DoiRepo.objects.get_doi_by_commit_id(repo_id, commit_id)
    if len(doi_repos) == 0:
        return render(request, '404.html')
    elif len(doi_repos) > 0 and doi_repos[0].rm is not None:
        return render(request, './catalog_detail/tombstone_page.html', {
            'doi': doi_repos[0].doi,
            'doi_dict': doi_repos[0].md
        })

    repo_owner = get_repo_owner(repo_id)
    cdc = False if get_cdc_id_by_repo(repo_id) is None else True
    link = "http://192.168.33.11/repo/history/view/" + repo_id + "/?commit_id=" + commit_id
    return render(request, './catalog_detail/landing_page.html', {
        'share_link': link,
        'cdc': cdc,
        'access': '',
        'commit_id': commit_id,
        'doi_dict': doi_repos[0].md,
        'doi': doi_repos[0].doi,
        'owner_contact_email': email2contact_email(repo_owner) })

def get_repo(repo_id): 
    return seafile_api.get_repo(repo_id)

def get_repo_owner(repo_id):
    return seafile_api.get_repo_owner(repo_id)

def get_cdc_id_by_repo(repo_id):
    """Get cdc_id by repo_id. Return None if nothing found"""
    return CDC.objects.get_cdc_id_by_repo(repo_id)