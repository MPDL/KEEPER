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
from keeper.models import CDC

from django.http import JsonResponse
from django.shortcuts import render

import logging
import datetime
import requests
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)

URL = "https://bloxberg.org/certifyData"
DOXI_URL = "https://test.doi.mpdl.mpg.de/"

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

def add_doi(request):
    repo_id = request.GET.get('repo_id', None)
    user_email = request.user.username
    metadata = get_metadata(repo_id, user_email)
    if metadata:
        return JsonResponse({'msg': str(metadata['Description'])})
    else:
        return JsonResponse({'msg': 'unable to read metadata'})
        
def CatalogDetailView(request, repo_id):
    logger.error(repo_id)
    repo = get_repo(repo_id)
    repo_owner = get_repo_owner(repo_id) 
    catalog = get_catalog_entry_by_repo_id(repo_id)
    cdc = False if get_cdc_id_by_repo(repo_id) is None else True

    if not repo:
        error_msg = 'Library %s not found.' % repo_id
        return api_error(status.HTTP_404_NOT_FOUND, error_msg)

    ## TBD should we include username
    username = request.user.username
    fileshares = FileShare.objects.filter(username=username)
    fileshares = filter(lambda fs: fs.repo_id == repo.id and fs.path == '/', fileshares)
    links_info = []
    for fs in fileshares:
        token = fs.token
        link = gen_shared_link(token, fs.s_type)
        links_info.append(link)

    if len(links_info) == 1:
        link = links_info[0]
    else:
        link = 'not avaliable'
    return render(request, './catalog_detail/landing_page_en.html', {
        'repo': repo,
        'owner_name': email2nickname(repo_owner),
        'share_link': link,
        'cdc': cdc,
        'access': '',
        'year': catalog.modified,
        'doi': '',
        'owner_contact_email': email2contact_email(repo_owner) })

def get_repo(repo_id): 
    return seafile_api.get_repo(repo_id)

def get_repo_owner(repo_id):
    return seafile_api.get_repo_owner(repo_id)

def get_cdc_id_by_repo(repo_id):
    """Get cdc_id by repo_id. Return None if nothing found"""
    return CDC.objects.get_cdc_id_by_repo(repo_id)    

def request_doxi():
    payload = "doix json"
    response = requests.post(DOXI_URL, json=payload)
    return