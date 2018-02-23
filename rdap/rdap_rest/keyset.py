"""Wrapper module to whois idl interface."""
from __future__ import unicode_literals

import logging
from urlparse import urljoin

from django.conf import settings
from django.urls import reverse

from .rdap_utils import ObjectClassName, nonempty, rdap_status_mapping, to_rfc3339


def keyset_to_dict(struct):
    """Transform CORBA keyset struct to python dictionary."""
    logging.debug(struct)

    if struct is None:
        result = None
    else:
        self_link = urljoin(settings.RDAP_ROOT_URL, reverse('keyset-detail', kwargs={"handle": struct.handle}))

        result = {
            "rdapConformance": ["rdap_level_0", "fred_version_0"],
            "objectClassName": ObjectClassName.KEYSET,
            "handle": struct.handle,
            "entities": [
                {
                    "objectClassName": ObjectClassName.ENTITY,
                    "handle": struct.registrar_handle,
                    "roles": ["registrar"],
                },
            ],
            "port43": settings.UNIX_WHOIS_HOST,
            "events": [
                {
                    "eventAction": "registration",
                    "eventDate": to_rfc3339(struct.created),
                },
            ],
            "links": [
                {
                    "value": self_link,
                    "rel": "self",
                    "href": self_link,
                    "type": "application/rdap+json",
                },
            ]
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

        if nonempty(struct.changed):
            result['events'].append({
                "eventAction": "last changed",
                "eventDate": to_rfc3339(struct.changed),
            })
        if nonempty(struct.last_transfer):
            result['events'].append({
                "eventAction": "transfer",
                "eventDate": to_rfc3339(struct.last_transfer),
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
