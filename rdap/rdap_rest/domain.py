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
from regal import Domain, ObjectEvents

from rdap.constants import ObjectStatus
from rdap.settings import CONTACT_CLIENT, DOMAIN_CLIENT, KEYSET_CLIENT, NSSET_CLIENT, RDAP_SETTINGS

from .rdap_utils import ObjectClassName, add_unicode_name, rdap_status_mapping, to_rfc3339


def domain_to_dict(domain: Domain, request: HttpRequest) -> Dict[str, Any]:
    """Transform domain to python dictionary."""
    logging.debug(domain)
    events = cast(ObjectEvents, domain.events)

    self_link = request.build_absolute_uri(reverse('domain-detail', kwargs={"handle": domain.fqdn}))
    result: Dict[str, Any] = {
        "objectClassName": ObjectClassName.DOMAIN,
        "rdapConformance": ["rdap_level_0", "fred_version_0"],
        "handle": domain.fqdn,
        "ldhName": domain.fqdn,
        "links": [
            {
                "value": self_link,
                "rel": "self",
                "href": self_link,
                "type": "application/rdap+json",
            },
        ],
    }

    if RDAP_SETTINGS.UNIX_WHOIS:
        result['port43'] = RDAP_SETTINGS.UNIX_WHOIS

    statuses = DOMAIN_CLIENT.get_domain_state(domain.domain_id)
    if statuses.get(ObjectStatus.DELETE_CANDIDATE, False):
        result['status'] = ["pending delete"]
    else:
        registrant = CONTACT_CLIENT.get_contact_info(domain.registrant)
        registrant_link = request.build_absolute_uri(
            reverse('entity-detail', kwargs={"handle": registrant.contact_handle}))

        result.update({
            "events": [
                {
                    "eventAction": "registration",
                    "eventDate": to_rfc3339(cast(datetime, events.registered.timestamp)),
                },
                {
                    "eventAction": "expiration",
                    "eventDate": to_rfc3339(cast(datetime, domain.expires_at)),
                },
            ],
            "entities": [
                {
                    "objectClassName": ObjectClassName.ENTITY,
                    "handle": registrant.contact_handle,
                    "roles": ["registrant"],
                    "links": [
                        {
                            "value": registrant_link,
                            "rel": "self",
                            "href": registrant_link,
                            "type": "application/rdap+json",
                        },
                    ]
                },
                {
                    "objectClassName": ObjectClassName.ENTITY,
                    "handle": domain.sponsoring_registrar,
                    "roles": ["registrar"],
                },
            ]
        })

        add_unicode_name(result, domain.fqdn)

        for admin_id in domain.administrative_contacts:
            contact = CONTACT_CLIENT.get_contact_info(admin_id)
            admin_link = request.build_absolute_uri(reverse('entity-detail', kwargs={"handle": contact.contact_handle}))
            result['entities'].append(
                {
                    "objectClassName": ObjectClassName.ENTITY,
                    "handle": contact.contact_handle,
                    "roles": ["administrative"],
                    "links": [
                        {
                            "value": admin_link,
                            "rel": "self",
                            "href": admin_link,
                            "type": "application/rdap+json",
                        },
                    ],
                }
            )
        result["status"] = rdap_status_mapping(tuple(s for s, f in statuses.items() if f))
        if events.updated:
            result['events'].append({
                "eventAction": 'last changed',
                "eventDate": to_rfc3339(cast(datetime, events.updated.timestamp)),
            })
        # transferred is always present, but may not have timestamp.
        if events.transferred.timestamp:
            result['events'].append({
                "eventAction": 'transfer',
                "eventDate": to_rfc3339(events.transferred.timestamp),
            })
        if domain.validation_expires_at:
            result['events'].append({
                "eventAction": 'enum validation expiration',
                "eventDate": to_rfc3339(domain.validation_expires_at),
            })

        if domain.nsset:
            nsset = NSSET_CLIENT.get_nsset_info(NSSET_CLIENT.get_nsset_id(domain.nsset))

            nsset_link = request.build_absolute_uri(reverse('nsset-detail', kwargs={"handle": nsset.nsset_handle}))
            result["nameservers"] = []
            result['fred_nsset'] = {
                "objectClassName": ObjectClassName.NSSET,
                "handle": nsset.nsset_handle,
                "links": [
                    {
                        "value": nsset_link,
                        "rel": "self",
                        "href": nsset_link,
                        "type": "application/rdap+json"
                    },
                ],
                "nameservers": [],
            }
            for ns in nsset.dns_hosts:
                ns_link = request.build_absolute_uri(reverse('nameserver-detail', kwargs={"handle": ns.fqdn}))
                ns_obj = {
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

                add_unicode_name(ns_obj, ns.fqdn)

                if ns.ip_addresses:
                    addrs_v4 = [str(a) for a in ns.ip_addresses if a.version == 4]
                    addrs_v6 = [str(a) for a in ns.ip_addresses if a.version == 6]
                    ns_obj["ipAddresses"] = {}
                    if addrs_v4:
                        ns_obj["ipAddresses"]["v4"] = addrs_v4
                    if addrs_v6:
                        ns_obj["ipAddresses"]["v6"] = addrs_v6
                result['nameservers'].append(ns_obj)
                result['fred_nsset']['nameservers'].append(ns_obj)

        if domain.keyset:
            keyset = KEYSET_CLIENT.get_keyset_info(KEYSET_CLIENT.get_keyset_id(domain.keyset))

            result["secureDNS"] = {
                "zoneSigned": True,
                "delegationSigned": True,
                "keyData": [],
            }
            if RDAP_SETTINGS.MAX_SIG_LIFE:
                result['secureDNS']['maxSigLife'] = RDAP_SETTINGS.MAX_SIG_LIFE
            keyset_link = request.build_absolute_uri(reverse('keyset-detail', kwargs={"handle": keyset.keyset_handle}))
            result['fred_keyset'] = {
                "objectClassName": ObjectClassName.KEYSET,
                "handle": keyset.keyset_handle,
                "links": [
                    {
                        "value": keyset_link,
                        "rel": "self",
                        "href": keyset_link,
                        "type": "application/rdap+json",
                    },
                ],
                "dns_keys": [],
            }
            for key in keyset.dns_keys:
                result["secureDNS"]['keyData'].append({
                    "flags": key.flags,
                    "protocol": key.protocol,
                    "algorithm": key.alg,
                    "publicKey": key.key,
                })
                result["fred_keyset"]['dns_keys'].append({
                    "flags": key.flags,
                    "protocol": key.protocol,
                    "algorithm": key.alg,
                    "publicKey": key.key,
                })

    logging.debug(result)
    return result
