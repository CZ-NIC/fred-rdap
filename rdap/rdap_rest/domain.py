"""
Wrapper module to whois idl interface
"""
import logging

from django.conf import settings
from django.utils.functional import SimpleLazyObject

from rdap.utils.corba import Corba, importIDL
from rdap.utils.corbarecoder import u2c, c2u
from .rdap_utils import unwrap_date, unwrap_datetime
from .rdap_utils import nonempty

importIDL('%s/%s' % (settings.CORBA_IDL_ROOT_PATH, settings.CORBA_IDL_WHOIS_FILENAME))
_CORBA = Corba(ior=settings.CORBA_NS_HOST_PORT, context_name=settings.CORBA_NS_CONTEXT,
               export_modules=settings.CORBA_EXPORT_MODULES)
_WHOIS = SimpleLazyObject(lambda: _CORBA.get_object('Whois2', 'Registry.Whois.WhoisIntf'))
_INTERFACE = _CORBA.Registry


def domain_to_dict(struct):
    """
    Transform CORBA domain struct to python dictionary
    """
    logging.debug(struct)

    if struct is None:
        result = None
    else:
        self_link = settings.RDAP_DOMAIN_URL_TMPL % {"handle": struct.handle}

        result = {
            "rdapConformance": ["rdap_level_0", "cznic_version_0"],
            "handle": struct.handle,
            "ldhName": struct.handle,
#            "unicodeName": struct.handle, # should be present only when containing non-ASCII chars
            "status": struct.statuses,
            "links": [
                {
                    "value": self_link,
                    "rel": "self",
                    "href": self_link,
                    "type": "application/rdap+json",
                },
            ],
            "port43": settings.UNIX_WHOIS_HOST,
            "events": [
                {
                    "eventAction": "registration",
                    "eventDate": unwrap_datetime(struct.registered),
                },
                {
                    "eventAction": "expiration",
                    "eventDate": unwrap_date(struct.expire),
                },
            ],
            "entities": [
                {
                    "handle": struct.registrant_handle,
                    "roles": ["registrant"],
                    "links": [
                        {
                            "value": settings.RDAP_ENTITY_URL_TMPL % {"handle": struct.registrant_handle},
                            "rel": "self",
                            "href": settings.RDAP_ENTITY_URL_TMPL % {"handle": struct.registrant_handle},
                            "type": "application/rdap+json",
                        },
                    ]
                },
                {
                    "handle": struct.registrar_handle,
                    "roles": ["registrar"],
                },
            ],
            "nameServers" : [],
        }

        for admin_contact in struct.admin_contact_handles:
            result['entities'].append(
                {
                    "handle": admin_contact,
                    "roles": ["administrative"],
                    "links": [
                        {
                            "value": settings.RDAP_ENTITY_URL_TMPL % {"handle": admin_contact},
                            "rel": "self",
                            "href": settings.RDAP_ENTITY_URL_TMPL % {"handle": admin_contact},
                            "type": "application/rdap+json",
                        },
                    ],
                }
            )
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
        if nonempty(struct.validated_to):
            result['events'].append({
                "eventAction": "enum validation expiration",
                "eventDate": unwrap_date(struct.validated_to),
            })
        if nonempty(struct.nsset_handle):
            nsset = c2u(_WHOIS.get_nsset_by_handle(u2c(struct.nsset_handle)))
            if nsset is not None:
                result['cznic_nsset'] = {
                    "handle": nsset.handle,
                    "links": [
                        {
                          "value": settings.RDAP_NSSET_URL_TMPL % {"handle": nsset.handle},
                          "rel": "self",
                          "href": settings.RDAP_NSSET_URL_TMPL % {"handle": nsset.handle},
                          "type": "application/rdap+json"
                        },
                    ],
                    "nameServers" : [],
                }
                for ns in nsset.nservers:
                    ns_obj = {
                        "handle": ns.fqdn,
                        "ldhName": ns.fqdn,
                        "links": [
                            {
                                "value": settings.RDAP_NAMESERVER_URL_TMPL % {"handle": ns.fqdn},
                                "rel": "self",
                                "href": settings.RDAP_NAMESERVER_URL_TMPL % {"handle": ns.fqdn},
                                "type": "application/rdap+json",
                            },
                        ],
                    }
                    if ns.ip_addresses:
                        addrs_v4 = []
                        addrs_v6 = []
                        for ip_addr in ns.ip_addresses:
                            if ip_addr.version._v == _CORBA.Registry.Whois.IPv4._v:
                                addrs_v4.append(ip_addr.address)
                            if ip_addr.version._v == _CORBA.Registry.Whois.IPv6._v:
                                addrs_v6.append(ip_addr.address)
                        ns_obj["ipAddresses"] = {}
                        if addrs_v4:
                            ns_obj["ipAddresses"]["v4"] = addrs_v4
                        if addrs_v6:
                            ns_obj["ipAddresses"]["v6"] = addrs_v6
                    result['nameServers'].append(ns_obj)
                    result['cznic_nsset']['nameServers'].append(ns_obj)

        if nonempty(struct.keyset_handle):
            keyset = c2u(_WHOIS.get_keyset_by_handle(u2c(struct.keyset_handle)))
            if keyset is not None:
                result["secureDNS"] = {
                    "zoneSigned": True,
                    "delegationSigned": True,
                    "maxSigLife": settings.DNS_MAX_SIG_LIFE,
                    "keyData": [],
                }
                result['cznic_keyset'] = {
                    "handle": keyset.handle,
                    "links": [
                        {
                          "value": settings.RDAP_KEYSET_URL_TMPL  % {"handle": keyset.handle},
                          "rel":"self",
                          "href": settings.RDAP_KEYSET_URL_TMPL  % {"handle": keyset.handle},
                          "type":"application/rdap+json",
                        },
                    ],
                    "dns_keys" : [],
                }
                for key in keyset.dns_keys:
                    result["secureDNS"]['keyData'].append({
                        "flags": key.flags,
                        "protocol": key.protocol,
                        "algorithm": key.alg,
                        "publicKey": key.public_key,
                    })
                    result["cznic_keyset"]['dns_keys'].append({
                        "flags": key.flags,
                        "protocol": key.protocol,
                        "algorithm": key.alg,
                        "publicKey": key.public_key,
                    })

    logging.debug(result)
    return result
