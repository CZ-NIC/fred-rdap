import logging
import traceback

from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.response import Response

from rdap.utils.py_logging import get_logger

from .rdap_utils import InvalidIdn, get_disclaimer_text, preprocess_fqdn
from .whois import InvalidHandleError, NotFoundError, get_contact_by_handle, get_domain_by_handle, \
    get_keyset_by_handle, get_nameserver_by_handle, get_nsset_by_handle


def translate_rest_path_to_request_type(path):
    if path == 'entity':
        return 'EntityLookup'
    if path == 'domain':
        return 'DomainLookup'
    if path == 'nameserver':
        return 'NameserverLookup'
    if path == 'fred_nsset':
        return 'NSSetLookup'
    if path == 'fred_keyset':
        return 'KeySetLookup'
    return ''


def create_log_request(path, handle, remote_addr):
    return get_logger().create_request(remote_addr, 'RDAP', translate_rest_path_to_request_type(path),
                                       [('handle', handle)], None, None, 'InternalServerError')


def response_handling(data_getter, getter_input_handle, log_request):
    try:
        rsp_content = None
        rsp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        log_content = ''
        log_status = 'InternalServerError'

        query_result = data_getter(getter_input_handle)

        if settings.DISCLAIMER_FILE:
            if 'notices' not in query_result:
                query_result["notices"] = []
            query_result["notices"].append(
                {
                    "title": "Disclaimer",
                    "description": [get_disclaimer_text()]
                }
            )

        rsp_content = query_result
        rsp_status = status.HTTP_200_OK
        log_status = 'Ok'
    except NotFoundError:
        rsp_status = status.HTTP_404_NOT_FOUND
        log_status = 'NotFound'
    except InvalidHandleError:
        rsp_status = status.HTTP_400_BAD_REQUEST
        log_status = 'BadRequest'
    except Exception, e:
        logging.debug(str(e))
        logging.debug(traceback.format_exc())
        rsp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        log_content = str(e)
        log_status = 'InternalServerError'
    finally:
        log_request.close(log_status, log_content)

    return Response(rsp_content, status=rsp_status, headers={'Access-Control-Allow-Origin': '*'})


class EntityViewSet(viewsets.ViewSet):
    """
    Entity View
    """
    def retrieve(self, request, handle=None, path=None):
        log_req = create_log_request(path, handle, request.META.get('REMOTE_ADDR', ''))
        return response_handling(
            get_contact_by_handle,
            handle,
            log_req
        )


class DomainViewSet(viewsets.ViewSet):
    """
    Domain View
    """
    def retrieve(self, request, handle=None, path=None):
        try:
            handle = preprocess_fqdn(handle)
        except InvalidIdn:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)
        log_req = create_log_request(path, handle, request.META.get('REMOTE_ADDR', ''))
        return response_handling(
            get_domain_by_handle,
            handle,
            log_req
        )


class NameserverViewSet(viewsets.ViewSet):
    """
    Nameserver View
    """
    def retrieve(self, request, handle=None, path=None):
        try:
            handle = preprocess_fqdn(handle)
        except InvalidIdn:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)
        log_req = create_log_request(path, handle, request.META.get('REMOTE_ADDR', ''))
        return response_handling(
            get_nameserver_by_handle,
            handle,
            log_req
        )


class NSSetViewSet(viewsets.ViewSet):
    """
    NSSet View
    """
    def retrieve(self, request, handle=None, path=None):
        log_req = create_log_request(path, handle, request.META.get('REMOTE_ADDR', ''))
        return response_handling(
            get_nsset_by_handle,
            handle,
            log_req
        )


class KeySetViewSet(viewsets.ViewSet):
    """
    KeySet View
    """
    def retrieve(self, request, handle=None, path=None):
        log_req = create_log_request(path, handle, request.META.get('REMOTE_ADDR', ''))
        return response_handling(
            get_keyset_by_handle,
            handle,
            log_req
        )


class MalformedRdapPathViewSet(viewsets.ViewSet):
    """
    MalformedRdapPath View
    """
    def retrieve(self, request, handle=None, path=None):
        return Response(None, status=status.HTTP_400_BAD_REQUEST)


class UnsupportedViewSet(viewsets.ViewSet):
    """
    Unsupported View
    """
    def retrieve(self, request, handle=None, path=None):
        return Response(None, status=status.HTTP_501_NOT_IMPLEMENTED)


class HelpViewSet(viewsets.ViewSet):
    """
    Help View
    """
    def retrieve(self, request):
        help_response = {
            "rdapConformance": ["rdap_level_0"],
            "notices": [
                {"title": "Help", "description": ["No help."]}
            ]
        }
        return Response(help_response, headers={'Access-Control-Allow-Origin': '*'})
