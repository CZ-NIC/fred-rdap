"""Wrapper module to whois idl interface."""
import logging

from django.conf import settings

from .rdap_utils import ObjectClassName, add_unicode_name


def nameserver_to_dict(struct):
    """Transform CORBA nameserver struct to python dictionary."""
    logging.debug(struct)

    if struct is None:
        result = None
    else:
        self_link = settings.RDAP_NAMESERVER_URL_TMPL % {"handle": struct.fqdn}

        result = {
          "rdapConformance": ["rdap_level_0"],
          "objectClassName": ObjectClassName.NAMESERVER,
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

        add_unicode_name(result, struct.fqdn)

    logging.debug(result)
    return result
