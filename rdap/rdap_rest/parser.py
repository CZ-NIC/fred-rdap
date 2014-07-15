from rest_framework.parsers import JSONParser
from rdap.rdap_rest.renderer import UnicodeRDAPJSONRenderer


class RDAPJSONParser(JSONParser):
    """
    Parser for RDAP+JSON media type
    """

    media_type = "application/rdap+json"
    renderer_class = UnicodeRDAPJSONRenderer

