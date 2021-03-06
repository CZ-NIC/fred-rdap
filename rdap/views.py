#
# Copyright (C) 2016-2020  CZ.NIC, z. s. p. o.
#
# This file is part of FRED.
#
# FRED is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FRED is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FRED.  If not, see <https://www.gnu.org/licenses/>.

"""RDAP views."""
from typing import Callable

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
from django.utils.functional import SimpleLazyObject
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from pylogger.corbalogger import Logger

from rdap.exceptions import InvalidHandleError, NotFoundError
from rdap.rdap_rest.rdap_utils import InvalidIdn, preprocess_fqdn
from rdap.settings import RDAP_SETTINGS
from rdap.utils.corba import LOGGER as LOGGER_OBJECT

RDAP_CONTENT_TYPE = 'application/rdap+json'
RDAP_CONFORMANCE = ['rdap_level_0', 'fred_version_0']

LOGGER = SimpleLazyObject(lambda: Logger(LOGGER_OBJECT))
LOGGER_SERVICE = 'RDAP'
LOGGER_SUCCESS = 'Ok'
LOGGER_NOT_FOUND = 'NotFound'
LOGGER_BAD_REQUEST = 'BadRequest'


class ObjectView(View):
    """View for RDAP protocol objects.

    @cvar getter: Function which returns object data or raises exception.
    @cvar request_type: Request type for logger
    """

    getter = None  # type: Callable
    request_type = None

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(ObjectView, self).dispatch(request, *args, **kwargs)

    def get(self, request, handle, *args, **kwargs):
        log_request = LOGGER.create_request(request.META.get('REMOTE_ADDR', ''), LOGGER_SERVICE, self.request_type,
                                            properties=[('handle', handle)])
        out_properties = []
        try:
            data = self.getter(request, handle)

            if RDAP_SETTINGS.DISCLAIMER:
                notices = data.setdefault('notices', [])
                notices.append({'title': 'Disclaimer', 'description': RDAP_SETTINGS.DISCLAIMER})

            log_request.result = LOGGER_SUCCESS
            response = JsonResponse(data, content_type=RDAP_CONTENT_TYPE)
            return response
        except NotFoundError:
            log_request.result = LOGGER_NOT_FOUND
            return HttpResponseNotFound(content_type=RDAP_CONTENT_TYPE)
        except InvalidHandleError:
            log_request.result = LOGGER_BAD_REQUEST
            return HttpResponseBadRequest(content_type=RDAP_CONTENT_TYPE)
        except Exception as error:
            out_properties.append(('error', type(error).__name__))
            raise error
        finally:
            log_request.close(properties=out_properties)


# TODO: IDN should be handled by backend. Once its implemented in FRED this view can be removed.
class FqdnObjectView(ObjectView):
    """View for domains and nameservers."""

    def get(self, request, handle, *args, **kwargs):
        try:
            handle = preprocess_fqdn(handle)
        except InvalidIdn:
            return HttpResponseBadRequest(content_type=RDAP_CONTENT_TYPE)
        return super(FqdnObjectView, self).get(request, handle, *args, **kwargs)


class HelpView(View):
    """Help view for RDAP protocol.

    @cvar help_text: The text to be displayed as a help.
    """

    help_text = 'See the API reference: https://fred.nic.cz/documentation/html/RDAPReference'

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(HelpView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        data = {
            'rdapConformance': RDAP_CONFORMANCE,
            'notices': [{'title': 'Help', 'description': [self.help_text]}],
        }
        response = JsonResponse(data, content_type=RDAP_CONTENT_TYPE)
        return response


class UnsupportedView(View):
    """View for unsupported responses.

    @cvar status: HTTP response code
    """

    status = 501

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(UnsupportedView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return HttpResponse(status=self.status, content_type=RDAP_CONTENT_TYPE)
