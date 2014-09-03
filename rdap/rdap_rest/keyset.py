"""
Wrapper module to whois idl interface
"""
import logging

from django.conf import settings
from django.utils.functional import SimpleLazyObject

from rdap.utils.corba import Corba, importIDL
from .rdap_utils import unwrap_datetime
from .rdap_utils import nonempty

importIDL(settings.CORBA_IDL_ROOT_PATH + '/' + settings.CORBA_IDL_WHOIS_FILENAME)

_CORBA = Corba(ior=settings.CORBA_NS_HOST_PORT, context_name=settings.CORBA_NS_CONTEXT,
               export_modules=settings.CORBA_EXPORT_MODULES)
_WHOIS = SimpleLazyObject(lambda: _CORBA.get_object('Whois2', 'Registry.Whois.WhoisIntf'))
_INTERFACE = _CORBA.Registry


def keyset_to_dict(struct):
    """
    Transform CORBA keyset struct to python dictionary
    """
    logging.debug(struct)

    if struct is None:
        result = None
    else:
        self_link = settings.RDAP_KEYSET_URL_TMPL  % {"handle": struct.handle}

        result = {
            "rdapConformance" : ["rdap_level_0", "cznic_version_0"],
            "handle": struct.handle,
            "entities": [
                {
                    "handle": struct.registrar_handle,
                    "roles": ["registrar"],
                },
            ],
            "port43": settings.UNIX_WHOIS_HOST,
            "events": [
                {
                    "eventAction" : "registration",
                    "eventDate" : unwrap_datetime(struct.created),
                },
            ],
            "links": [
                {
                    "value": self_link,
                    "rel":"self",
                    "href": self_link,
                    "type":"application/rdap+json",
                },
            ]
        }

        if struct.statuses:
            result["status"] = struct.statuses

        for tech_c in struct.tech_contact_handles:
            result['entities'].append({
                "handle": tech_c,
                "roles": ["technical"],
                "links": [
                    {
                        "value": settings.RDAP_ENTITY_URL_TMPL % {"handle": tech_c},
                        "rel": "self",
                        "href": settings.RDAP_ENTITY_URL_TMPL % {"handle": tech_c},
                        "type": "application/rdap+json",
                    },
                ],
            })

        if nonempty(struct.changed):
            result['events'].append({
                "eventAction": "last changed",
                "eventDate": unwrap_datetime(struct.changed),
            })
        if nonempty(struct.last_transfer):
            result['events'].append({
                "eventAction": "transfer",
                "eventDate": unwrap_datetime(struct.last_transfer),
            })

        if struct.dns_keys:
            result["dns_keys"] = []
            for key in struct.dns_keys:
                result['dns_keys'].append({
                    "flags": key.flags,
                    "protocol": key.protocol,
                    "algorithm": key.alg,
                    "publicKey": key.public_key,
                })

    logging.debug(result)
    return result
