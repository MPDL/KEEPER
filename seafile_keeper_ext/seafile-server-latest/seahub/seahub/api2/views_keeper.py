from rest_framework.views import APIView
from rest_framework import status

from seahub import settings
from seahub.base.templatetags.seahub_tags import email2nickname, email2contact_email
from seahub.api2.utils import json_response, api_error
from seahub.share.models import FileShare
from seahub.utils import gen_shared_link
from seaserv import seafile_api

from keeper.catalog.catalog_manager import get_catalog, get_catalog_entry_by_repo_id
from keeper.bloxberg.bloxberg_manager import hash_file, create_bloxberg_certificate
from keeper.doi.doi_manager import get_metadata
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
        user='keeper_test'
        pwd='4PsYQ_788%sd'
        headers = {'Content-Type': 'text/xml'}
        response = requests.put(DOXI_URL, auth=(user, pwd), headers=headers, params={'url': shared_link}, data=doxi_payload)
        return response
    except ConnectionError as e:
        logger.error(str(e))

def add_doi(request):
    repo_id = request.GET.get('repo_id', None)
    user_email = request.user.username
    metadata = get_metadata(repo_id, user_email)
    shared_link = get_shared_link(user_email, repo_id)
    logger.info(metadata)
    logger.info(shared_link)
    if shared_link == 'not avaliable':
        return JsonResponse({'msg': 'lib not shared'})

    # delete
    repo = get_repo(repo_id)
    repo_name = repo.name
    repo_owner = get_repo_owner(repo_id)

    DoiRepo.objects.add_doi_repo(repo_id, repo_name, 'https://doi.org/10.15771/5.28m', None, '057c81f004fab23082ec32bd804225c5df3f9f3b', repo_owner)
    
    doi_repo = DoiRepo.objects.get_doi_repo(repo_id, '057c81f004fab23082ec32bd804225c5df3f9f3b')
    
    if doi_repo is not None:
        logger.info(doi_repo)
        logger.info(doi_repo.doi)
        return JsonResponse({'msg': 'Doi  exists: ' + doi_repo.doi})
    else:
        logger.info("doiRepo is None")
        return JsonResponse({'msg': 'Doi is none: '})

    response_doxi = request_doxi(shared_link, metadata)

    if response_doxi is not None:
        if response_doxi.status_code == 201:
            doi = response_doxi.text
            logger.info(doi)
            #todo: add to doi
            return JsonResponse({'msg': 'Create DOI successful: ' + doi})
        else:
            logger.info(response_doxi.status_code)
            logger.info(response_doxi.text)
            return JsonResponse({'msg': 'Failed to create DOI: ' + response_doxi.text})
        
def DoiView(request, doi):
    repo_id = '9a3e3d8b-9448-4328-9aa3-9dd4990dc00c'
    repo = get_repo(repo_id)
    repo_owner = get_repo_owner(repo_id) 
    catalog = get_catalog_entry_by_repo_id(repo_id)
    cdc = False if get_cdc_id_by_repo(repo_id) is None else True

    if not repo:
        error_msg = 'Library %s not found.' % repo_id
        return api_error(status.HTTP_404_NOT_FOUND, error_msg)

    ## TBD should we include username
    link = get_shared_link(request.user.username, repo_id)
    return render(request, './catalog_detail/landing_page.html', {
        'repo': repo,
        'owner_name': email2nickname(repo_owner),
        'share_link': link,
        'cdc': cdc,
        'access': '',
        'year': catalog.modified,
        'doi': doi,
        'owner_contact_email': email2contact_email(repo_owner) })

def get_repo(repo_id): 
    return seafile_api.get_repo(repo_id)

def get_repo_owner(repo_id):
    return seafile_api.get_repo_owner(repo_id)

def get_cdc_id_by_repo(repo_id):
    """Get cdc_id by repo_id. Return None if nothing found"""
    return CDC.objects.get_cdc_id_by_repo(repo_id)    

def get_shared_link(username, repo_id):
    fileshares = FileShare.objects.filter(username=username)
    fileshares = filter(lambda fs: fs.repo_id == repo_id and fs.path == '/', fileshares)
    links_info = []
    for fs in fileshares:
        token = fs.token
        link = gen_shared_link(token, fs.s_type)
        links_info.append(link)

    if len(links_info) == 1:
        link = links_info[0]
    else:
        link = 'not avaliable'
    return link