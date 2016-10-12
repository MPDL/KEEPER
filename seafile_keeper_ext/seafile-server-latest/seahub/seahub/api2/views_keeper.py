from rest_framework.views import APIView

from seahub.api2.utils import json_response
from seahub import settings

from keeper.catalog_manager import get_catalog 

from seahub import settings

class CatalogView(APIView):
    """
    Returns Keeper Catalog.
    """
    @json_response
    def get(self, request, format=None):
        catalog = get_catalog()
        return catalog
