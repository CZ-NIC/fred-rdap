from rest_framework.renderers import JSONRenderer


class RDAPJSONRenderer(JSONRenderer):
    """
    Renderer which serialize to JSON but uses RDAP specific media type
    """

    media_type = 'application/rdap+json'
