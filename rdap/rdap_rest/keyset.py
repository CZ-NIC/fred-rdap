#
# Copyright (C) 2014-2022  CZ.NIC, z. s. p. o.
#
# This file is part of FRED.
#
# FRED is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FRED is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FRED.  If not, see <https://www.gnu.org/licenses/>.
#
"""Wrapper module to whois idl interface."""
import logging
from datetime import datetime
from typing import Any, Dict, cast

from django.http import HttpRequest
from django.urls import reverse
from regal import Keyset, ObjectEvents

from rdap.settings import CONTACT_CLIENT, KEYSET_CLIENT, RDAP_SETTINGS

from .rdap_utils import ObjectClassName, rdap_status_mapping, to_rfc3339


def keyset_to_dict(keyset: Keyset, request: HttpRequest) -> Dict[str, Any]:
    """Transform CORBA keyset keyset to python dictionary."""
    logging.debug(keyset)
    events = cast(ObjectEvents, keyset.events)

    self_link = request.build_absolute_uri(reverse('keyset-detail', kwargs={"handle": keyset.keyset_handle}))

    result: Dict[str, Any] = {
        "rdapConformance": ["rdap_level_0", "fred_version_0"],
        "objectClassName": ObjectClassName.KEYSET,
        "handle": keyset.keyset_handle,
        "entities": [
            {
                "objectClassName": ObjectClassName.ENTITY,
                "handle": keyset.sponsoring_registrar,
                "roles": ["registrar"],
            },
        ],
        "events": [
            {
                "eventAction": "registration",
                "eventDate": to_rfc3339(cast(datetime, events.registered.timestamp)),
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
    if RDAP_SETTINGS.UNIX_WHOIS:
        result['port43'] = RDAP_SETTINGS.UNIX_WHOIS

    statuses = KEYSET_CLIENT.get_keyset_state(keyset.keyset_id)
    result["status"] = rdap_status_mapping(tuple(s for s, f in statuses.items() if f))

    for tech_id in keyset.technical_contacts:
        contact = CONTACT_CLIENT.get_contact_info(tech_id)
        tech_link = request.build_absolute_uri(reverse('entity-detail', kwargs={"handle": contact.contact_handle}))
        result['entities'].append({
            "objectClassName": ObjectClassName.ENTITY,
            "handle": contact.contact_handle,
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

    if events.updated:
        result['events'].append({
            "eventAction": "last changed",
            "eventDate": to_rfc3339(cast(datetime, events.updated.timestamp)),
        })
    # transferred is always present, but may not have timestamp.
    if events.transferred.timestamp:
        result['events'].append({
            "eventAction": "transfer",
            "eventDate": to_rfc3339(events.transferred.timestamp),
        })

    if keyset.dns_keys:
        result["dns_keys"] = []
        for key in keyset.dns_keys:
            result['dns_keys'].append({
                "flags": key.flags,
                "protocol": key.protocol,
                "algorithm": key.alg,
                "publicKey": key.key,
            })

    logging.debug(result)
    return result
