from rest_framework.views import APIView

from seahub.api2.utils import json_response
from seahub import settings

from keeper.catalog.catalog_manager import get_catalog

from keeper.bloxberg.bloxberg_manager import hash_file, create_bloxberg_certificate

from django.http import JsonResponse

import sys
import logging

import seaserv
import datetime
import requests
from requests.exceptions import ConnectionError

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
    hash_data = hash_file(repo_id, path)

    response_bloxberg = request_bloxberg(hash_data);
    if response_bloxberg is not None:
        if response_bloxberg.status_code == 200:
            transaction_id = response_bloxberg.json()['txReceipt']['tx']
            checksum = hash_data['certifyVariables']['checksum']
            created_time = datetime.datetime.utcfromtimestamp(float(hash_data['certifyVariables']['timestampString']))
            create_bloxberg_certificate(repo_id, path, transaction_id, created_time, checksum)
            return JsonResponse(response_bloxberg.json())

    return JsonResponse({'msg': 'Transaction failed'})

def request_bloxberg(certify_payload):
    try:
        response = requests.post('https://bloxberg.org/certifyData', json=certify_payload)
        return response
    except ConnectionError as e:
        logger.error(str(e))

