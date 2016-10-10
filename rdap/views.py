"""
RDAP views.
"""
from django.http import HttpResponse, JsonResponse
from django.views.generic import View

RDAP_CONTENT_TYPE = 'application/rdap+json'
RDAP_CONFORMANCE = ['rdap_level_0', 'fred_version_0']


class HelpView(View):
    """
    Help view for RDAP protocol.
    """
    def get(self, request, *args, **kwargs):
        data = {
            'rdapConformance': RDAP_CONFORMANCE,
            'notices': [{'title': 'Help', 'description': ['No help.']}],
        }
        response = JsonResponse(data, content_type=RDAP_CONTENT_TYPE)
        response['Access-Control-Allow-Origin'] = '*'
        return response


class UnsupportedView(View):
    """
    View for unsupported responses.

    @cvar status: HTTP response code
    """
    status = 501

    def get(self, request, *args, **kwargs):
        return HttpResponse(status=self.status, content_type=RDAP_CONTENT_TYPE)
