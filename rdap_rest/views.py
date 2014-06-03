import logging
import traceback

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response

from rdap_rest.whois import *

def response_handling(query_result):
    try:
        if query_result is None:
            return Response(None, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(query_result)
    except Exception, e:
        logging.debug(str(e))
        logging.debug(traceback.format_exc())
        return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EntityViewSet(viewsets.ViewSet):
    """
    Entity View
    """
    def retrieve(self, request, handle=None):
        return response_handling(whois_get_contact_by_handle(str(handle)))
            
class DomainViewSet(viewsets.ViewSet):
    """
    Domain View
    """
    def retrieve(self, request, handle=None):
        return response_handling(whois_get_domain_by_handle(str(handle)))

class NameserverViewSet(viewsets.ViewSet):
    """
    Nameserver View
    """
    def retrieve(self, request, handle=None):
        return response_handling(whois_get_nameserver_by_handle(str(handle)))
