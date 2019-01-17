from rest_framework.views import APIView

from seahub.api2.utils import json_response
from seahub import settings

from keeper.catalog.catalog_manager import get_catalog

from keeper.bloxberg.bloxberg_manager import hash_file, create_bloxberg_certificate

from django.http import JsonResponse
import sys
import logging

import seaserv


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
    data = hash_file(repo_id, path)
    return JsonResponse(data)


def add_bloxberg_certificate(request):
    repo_id = request.GET.get('repo_id', None)
    path = request.GET.get('path', None)
    transaction_id = request.GET.get('transaction_id', None)
    created_time = request.GET.get('created_time', None)

    logger.error(created_time)

    data = create_bloxberg_certificate(repo_id, path, transaction_id, created_time)
    return JsonResponse(data)

