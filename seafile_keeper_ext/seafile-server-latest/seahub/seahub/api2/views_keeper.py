from rest_framework.views import APIView

from seahub.api2.utils import json_response
from seahub import settings

from keeper.catalog.catalog_manager import get_catalog, get_catalog_entry_by_repo_id
from keeper.bloxberg.bloxberg_manager import hash_file, create_bloxberg_certificate
from keeper.doi.doi_manager import get_metadata
from django.http import JsonResponse

import sys
import logging

import seaserv
import datetime
import requests
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)

URL = "https://bloxberg.org/certifyData"
from django.shortcuts import render

import seaserv
from seaserv import seafile_api

from seahub.base.templatetags.seahub_tags import email2nickname, email2contact_email
import logging
from django.http import Http404
from keeper.models import CDC


logger = logging.getLogger(__name__)

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
    metadata = get_metadata(repo_id)
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

    if repo is None:
        raise Http404("repository does not exist")

    size = repo.size    
    if repo.size > 1000000000:
        size = "{0:.2f} GB".format(repo.size / 1000000000.00)
    elif repo.size > 1000000:
        size = "{0:.2f} MB".format(repo.size / 1000000.00) 
    elif repo.size > 1000:
        size = "{0:.2f} KB".format(repo.size / 1000.00)

    return render(request, './catalog_detail/landing_page_en.html', {
        'repo': repo,
        'owner_name':  email2nickname(repo_owner),
        'size': size,
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
