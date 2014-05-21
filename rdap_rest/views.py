import logging
import traceback

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response

from rdap_rest.whois import whois_get_contact_by_handle



class EntityViewSet(viewsets.ViewSet):
    """
    Just testing prototype of rdap entity view
    """
    def retrieve(self, request, handle=None):
        """
        Get entity detail by handle

        XXX: all responses are not rdap valid and so far are used just for testing rest framework
        """
        try:
            return Response(whois_get_contact_by_handle(str(handle)))
        except Exception, e:
            logging.debug(str(e))
            logging.debug(traceback.format_exc())
            return Response(None, status=status.HTTP_404_NOT_FOUND)


    def list(self, request):
        """
        Search entity by handle or name
        """
        if request.GET.get('handle'):
            return Response({'request': 'entity-list', 'handle': request.GET['handle']})
        elif request.GET.get('fn'):
            return Response({'request': 'entity-list', 'fn': request.GET['fn']})
        return Response(None, status=status.HTTP_404_NOT_FOUND)

