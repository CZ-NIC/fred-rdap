"""
Wrapper module to whois idl interface
"""
import logging

from django.conf import settings


def nameserver_to_dict(struct):
    """
    Transform CORBA nameserver struct to python dictionary
    """
    logging.debug(struct)

    if struct is None:
        result = None
    else:
        self_link = settings.RDAP_NAMESERVER_URL_TMPL % {"handle": struct.fqdn}

        result = {
          "rdapConformance": ["rdap_level_0"],
          "objectClassName": "nameserver",
          "handle": struct.fqdn,
          "ldhName": struct.fqdn,
          "links": [
              {
                  "value": self_link,
                  "rel": "self",
                  "href": self_link,
                  "type": "application/rdap+json",
              },
          ],
        }

    logging.debug(result)
    return result
