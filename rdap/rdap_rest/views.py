import logging
import traceback

from rest_framework import viewsets, status
from rest_framework.response import Response

from .whois import get_contact_by_handle, get_domain_by_handle, get_keyset_by_handle, get_nameserver_by_handle, \
    get_nsset_by_handle
from rdap.utils.py_logging import get_logger


def translate_rest_path_to_request_type(path):
    if path == 'entity':
        return 'EntityLookup'
    if path == 'domain':
        return 'DomainLookup'
    if path == 'nameserver':
        return 'NameserverLookup'
    if path == 'cznic_nsset':
        return 'NSSetLookup'
    if path == 'cznic_keyset':
        return 'KeySetLookup'
    return ''


def create_log_request(path, handle, remote_addr):
    return get_logger().create_request(remote_addr, 'RDAP', translate_rest_path_to_request_type(path),
                                       [('handle', handle)], None, None, 'InternalServerError')


def response_handling(query_result, log_request):
    try:
        if query_result is None:
            log_request.close('NotFound')
            return Response(None, status=status.HTTP_404_NOT_FOUND)
        else:
            log_request.close('Ok')
            return Response(query_result)
    except Exception, e:
        logging.debug(str(e))
        logging.debug(traceback.format_exc())
        log_request.close('InternalServerError')
        return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EntityViewSet(viewsets.ViewSet):
    """
    Entity View
    """
    def retrieve(self, request, handle=None, path=None):
        return response_handling(
            get_contact_by_handle(str(handle)),
            create_log_request(path, handle, request.META.get('REMOTE_ADDR', ''))
        )


class DomainViewSet(viewsets.ViewSet):
    """
    Domain View
    """
    def retrieve(self, request, handle=None, path=None):
        return response_handling(
            get_domain_by_handle(str(handle)),
            create_log_request(path, handle, request.META.get('REMOTE_ADDR', ''))
        )


class NameserverViewSet(viewsets.ViewSet):
    """
    Nameserver View
    """
    def retrieve(self, request, handle=None, path=None):
        return response_handling(
            get_nameserver_by_handle(str(handle)),
            create_log_request(path, handle, request.META.get('REMOTE_ADDR', ''))
        )


class NSSetViewSet(viewsets.ViewSet):
    """
    NSSet View
    """
    def retrieve(self, request, handle=None, path=None):
        return response_handling(
            get_nsset_by_handle(str(handle)),
            create_log_request(path, handle, request.META.get('REMOTE_ADDR', ''))
        )


class KeySetViewSet(viewsets.ViewSet):
    """
    KeySet View
    """
    def retrieve(self, request, handle=None, path=None):
        return response_handling(
            get_keyset_by_handle(str(handle)),
            create_log_request(path, handle, request.META.get('REMOTE_ADDR', ''))
        )


class MalformedRdapPath(viewsets.ViewSet):
    """
    MalformedRdapPath View
    """
    def retrieve(self, request, handle=None, path=None):
        return Response(None, status=status.HTTP_400_BAD_REQUEST)


class NotFound(viewsets.ViewSet):
    """
    NotFound View
    """
    def retrieve(self, request, handle=None, path=None):
        create_log_request(path, handle, request.META.get('REMOTE_ADDR', '')).close('NotFound')
        return Response(None, status=status.HTTP_404_NOT_FOUND)
