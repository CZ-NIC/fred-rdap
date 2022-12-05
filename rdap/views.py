#
# Copyright (C) 2016-2022  CZ.NIC, z. s. p. o.
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
#
"""RDAP views."""
from typing import Any, Callable, cast

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from grill import Logger, get_logger_client
from regal.exceptions import ObjectDoesNotExist

from rdap.rdap_rest.rdap_utils import InvalidIdn, preprocess_fqdn
from rdap.settings import RDAP_SETTINGS

from .constants import LOGGER_SERVICE, LogResult

RDAP_CONTENT_TYPE = 'application/rdap+json'
RDAP_CONFORMANCE = ['rdap_level_0', 'fred_version_0']

_LOGGER_CLIENT = get_logger_client(RDAP_SETTINGS.LOGGER, **RDAP_SETTINGS.LOGGER_OPTIONS)
LOGGER = Logger(_LOGGER_CLIENT, LOGGER_SERVICE, LogResult.INTERNAL_SERVER_ERROR)


class ObjectView(View):
    """View for RDAP protocol objects.

    @cvar getter: Function which returns object data or raises exception.
    @cvar request_type: Request type for logger
    """

    getter: Callable = None  # type: ignore[assignment]  # not ideal, but backward compatible
    request_type = None

    @csrf_exempt
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super(ObjectView, self).dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, handle: str, *args: Any, **kwargs: Any) -> HttpResponse:
        with LOGGER.create(cast(str, self.request_type), source_ip=request.META.get('REMOTE_ADDR', ''),
                           properties={'handle': handle}) as log_entry:
            try:
                data = self.getter(request, handle)

                if RDAP_SETTINGS.DISCLAIMER:
                    notices = data.setdefault('notices', [])
                    notices.append({'title': 'Disclaimer', 'description': RDAP_SETTINGS.DISCLAIMER})

                log_entry.result = LogResult.SUCCESS
                return JsonResponse(data, content_type=RDAP_CONTENT_TYPE)

            except ObjectDoesNotExist:
                log_entry.result = LogResult.NOT_FOUND
                return HttpResponseNotFound(content_type=RDAP_CONTENT_TYPE)
            except Exception as error:
                log_entry.properties = {'error': type(error).__name__}
                raise error


# TODO: IDN should be handled by backend. Once its implemented in FRED this view can be removed.
class FqdnObjectView(ObjectView):
    """View for domains and nameservers."""

    def get(self, request: HttpRequest, handle: str, *args: Any, **kwargs: Any) -> HttpResponse:
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
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super(HelpView, self).dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
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
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super(UnsupportedView, self).dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return HttpResponse(status=self.status, content_type=RDAP_CONTENT_TYPE)
