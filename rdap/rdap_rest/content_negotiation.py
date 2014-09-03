from rest_framework.negotiation import BaseContentNegotiation
from renderer import UnicodeRDAPJSONRenderer

class RdapJsonForAllContentNegotiation(BaseContentNegotiation):
    def select_renderer(self, request, renderers, format_suffix):
        """
        http://tools.ietf.org/html/draft-ietf-weirds-using-http-08#section-4.1:
        "Servers receiving an RDAP request return an entity with a Content-Type: header containing the RDAP specific JSON media type."
        "This specification does not define the responses a server returns to a request with any other media types in the Accept: header field, or with no Accept: header field."
        """
        for renderer in renderers:
            if isinstance(renderer, UnicodeRDAPJSONRenderer):
                return (renderer, renderer.media_type)

        raise Exception("Missing UnicodeRDAPJSONRenderer!")
