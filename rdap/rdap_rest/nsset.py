"""Wrapper module to whois idl interface."""
import logging
from urlparse import urljoin

from django.conf import settings

from rdap.utils.corba import REGISTRY_MODULE

from .rdap_utils import ObjectClassName, add_unicode_name, nonempty, rdap_status_mapping, to_rfc3339, unwrap_datetime

try:
    from django.urls import reverse
except ImportError:
    # Support Django < 1.10
    from django.core.urlresolvers import reverse


def nsset_to_dict(struct):
    """Transform CORBA nsset struct to python dictionary."""
    logging.debug(struct)

    if struct is None:
        result = None
    else:
        self_link = urljoin(settings.RDAP_ROOT_URL, reverse('nsset-detail', kwargs={"handle": struct.handle}))

        result = {
            "rdapConformance": ["rdap_level_0", "fred_version_0"],
            "objectClassName": ObjectClassName.NSSET,
            "handle": struct.handle,
            "entities": [
                {
                    "objectClassName": ObjectClassName.ENTITY,
                    "handle": struct.registrar_handle,
                    "roles": ["registrar"],
                }
            ],
            "port43": settings.UNIX_WHOIS_HOST,
            "events": [
                {
                    "eventAction": "registration",
                    "eventDate": to_rfc3339(unwrap_datetime(struct.created)),
                }
            ],
            "links": [
                {
                    "value": self_link,
                    "rel": "self",
                    "href": self_link,
                    "type": "application/rdap+json",
                },
            ],
            "nameservers": [],
        }

        status = rdap_status_mapping(struct.statuses)
        if status:
            result["status"] = status

        for tech_c in struct.tech_contact_handles:
            tech_link = urljoin(settings.RDAP_ROOT_URL, reverse('entity-detail', kwargs={"handle": tech_c}))
            result['entities'].append({
                "objectClassName": ObjectClassName.ENTITY,
                "handle": tech_c,
                "roles": ["technical"],
                "links": [
                    {
                        "value": tech_link,
                        "rel": "self",
                        "href": tech_link,
                        "type": "application/rdap+json",
                    },
                ],
            })

        for ns in struct.nservers:
            ns_link = urljoin(settings.RDAP_ROOT_URL, reverse('nameserver-detail', kwargs={"handle": ns.fqdn}))
            ns_json = {
                "objectClassName": ObjectClassName.NAMESERVER,
                "handle": ns.fqdn,
                "ldhName": ns.fqdn,
                "links": [
                    {
                        "value": ns_link,
                        "rel": "self",
                        "href": ns_link,
                        "type": "application/rdap+json",
                    },
                ],
            }

            add_unicode_name(ns_json, ns.fqdn)

            if ns.ip_addresses:
                addrs_v4 = []
                addrs_v6 = []
                for ip_addr in ns.ip_addresses:
                    if ip_addr.version._v == REGISTRY_MODULE.Whois.IPv4._v:
                        addrs_v4.append(ip_addr.address)
                    if ip_addr.version._v == REGISTRY_MODULE.Whois.IPv6._v:
                        addrs_v6.append(ip_addr.address)
                ns_json["ipAddresses"] = {}
                if addrs_v4:
                    ns_json["ipAddresses"]["v4"] = addrs_v4
                if addrs_v6:
                    ns_json["ipAddresses"]["v6"] = addrs_v6

            result['nameservers'].append(ns_json)

        if nonempty(struct.changed):
            result['events'].append({
                "eventAction": "last changed",
                "eventDate": to_rfc3339(unwrap_datetime(struct.changed)),
            })
        if nonempty(struct.last_transfer):
            result['events'].append({
                "eventAction": "transfer",
                "eventDate": to_rfc3339(unwrap_datetime(struct.last_transfer)),
            })

    logging.debug(result)
    return result
