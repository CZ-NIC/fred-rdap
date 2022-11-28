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
from regal import Nsset, ObjectEvents

from rdap.settings import RDAP_SETTINGS
from rdap.utils.corba import CONTACT_CLIENT, NSSET_CLIENT

from .rdap_utils import ObjectClassName, add_unicode_name, rdap_status_mapping, to_rfc3339


def nsset_to_dict(nsset: Nsset, request: HttpRequest) -> Dict[str, Any]:
    """Transform nsset to python dictionary."""
    logging.debug(nsset)
    events = cast(ObjectEvents, nsset.events)

    self_link = request.build_absolute_uri(reverse('nsset-detail', kwargs={"handle": nsset.nsset_handle}))

    result: Dict[str, Any] = {
        "rdapConformance": ["rdap_level_0", "fred_version_0"],
        "objectClassName": ObjectClassName.NSSET,
        "handle": nsset.nsset_handle,
        "entities": [
            {
                "objectClassName": ObjectClassName.ENTITY,
                "handle": nsset.sponsoring_registrar,
                "roles": ["registrar"],
            }
        ],
        "events": [
            {
                "eventAction": "registration",
                "eventDate": to_rfc3339(cast(datetime, events.registered.timestamp)),
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
    if RDAP_SETTINGS.UNIX_WHOIS:
        result['port43'] = RDAP_SETTINGS.UNIX_WHOIS

    statuses = NSSET_CLIENT.get_nsset_state(nsset.nsset_id)
    result["status"] = rdap_status_mapping(tuple(s for s, f in statuses.items() if f))

    for tech_id in nsset.technical_contacts:
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

    for ns in nsset.dns_hosts:
        ns_link = request.build_absolute_uri(reverse('nameserver-detail', kwargs={"handle": ns.fqdn}))
        ns_json: Dict[str, Any] = {
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
            addrs_v4 = [str(a) for a in ns.ip_addresses if a.version == 4]
            addrs_v6 = [str(a) for a in ns.ip_addresses if a.version == 6]
            ns_json["ipAddresses"] = {}
            if addrs_v4:
                ns_json["ipAddresses"]["v4"] = addrs_v4
            if addrs_v6:
                ns_json["ipAddresses"]["v6"] = addrs_v6

        result['nameservers'].append(ns_json)

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

    logging.debug(result)
    return result
