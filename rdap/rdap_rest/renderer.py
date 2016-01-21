from rest_framework.renderers import UnicodeJSONRenderer


class UnicodeRDAPJSONRenderer(UnicodeJSONRenderer):
    """
    Renderer which serialize to JSON but uses RDAP specific media type
    """

    media_type = 'application/rdap+json'
