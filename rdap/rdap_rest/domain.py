#
# Copyright (C) 2014-2020  CZ.NIC, z. s. p. o.
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

"""Wrapper module to whois idl interface."""

import logging

from django.urls import reverse
from fred_idl.Registry.Whois import IPv4, IPv6

from rdap.settings import RDAP_SETTINGS
from rdap.utils.corba import WHOIS

from .rdap_utils import ObjectClassName, add_unicode_name, nonempty, rdap_status_mapping, to_rfc3339


def domain_to_dict(request, struct):
    """Transform CORBA domain struct to python dictionary."""
    logging.debug(struct)

    if struct is None:
        result = None
    else:
        if struct.expire_time_actual:
            expiration_datetime = struct.expire_time_actual
        else:
            expiration_datetime = struct.expire_time_estimate

        self_link = request.build_absolute_uri(reverse('domain-detail', kwargs={"handle": struct.handle}))
        registrant_link = request.build_absolute_uri(
            reverse('entity-detail', kwargs={"handle": struct.registrant_handle}))

        result = {
            "rdapConformance": ["rdap_level_0", "fred_version_0"],
            "objectClassName": ObjectClassName.DOMAIN,
            "handle": struct.handle,
            "ldhName": struct.handle,
            "links": [
                {
                    "value": self_link,
                    "rel": "self",
                    "href": self_link,
                    "type": "application/rdap+json",
                },
            ],
            "events": [
                {
                    "eventAction": "registration",
                    "eventDate": to_rfc3339(struct.registered),
                },
                {
                    "eventAction": "expiration",
                    "eventDate": to_rfc3339(expiration_datetime),
                },
            ],
            "entities": [
                {
                    "objectClassName": ObjectClassName.ENTITY,
                    "handle": struct.registrant_handle,
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
                    "handle": struct.registrar_handle,
                    "roles": ["registrar"],
                },
            ]
        }
        if RDAP_SETTINGS.UNIX_WHOIS:
            result['port43'] = RDAP_SETTINGS.UNIX_WHOIS

        add_unicode_name(result, struct.handle)

        for admin_contact in struct.admin_contact_handles:
            admin_link = request.build_absolute_uri(reverse('entity-detail', kwargs={"handle": admin_contact}))
            result['entities'].append(
                {
                    "objectClassName": ObjectClassName.ENTITY,
                    "handle": admin_contact,
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
        status = rdap_status_mapping(struct.statuses)
        if status:
            result["status"] = status
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
        if struct.validated_to_time_actual:
            validated_to_datetime = struct.validated_to_time_actual
        elif struct.validated_to_time_estimate:
            validated_to_datetime = struct.validated_to_time_estimate
        else:
            validated_to_datetime = None
        if validated_to_datetime:
            result['events'].append({
                "eventAction": "enum validation expiration",
                "eventDate": to_rfc3339(validated_to_datetime),
            })
        if nonempty(struct.nsset_handle):
            nsset = WHOIS.get_nsset_by_handle(struct.nsset_handle)
            if nsset is not None:
                nsset_link = request.build_absolute_uri(reverse('nsset-detail', kwargs={"handle": nsset.handle}))
                result["nameservers"] = []
                result['fred_nsset'] = {
                    "objectClassName": ObjectClassName.NSSET,
                    "handle": nsset.handle,
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
                for ns in nsset.nservers:
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
                        addrs_v4 = []
                        addrs_v6 = []
                        for ip_addr in ns.ip_addresses:
                            if ip_addr.version._v == IPv4._v:
                                addrs_v4.append(ip_addr.address)
                            if ip_addr.version._v == IPv6._v:
                                addrs_v6.append(ip_addr.address)
                        ns_obj["ipAddresses"] = {}
                        if addrs_v4:
                            ns_obj["ipAddresses"]["v4"] = addrs_v4
                        if addrs_v6:
                            ns_obj["ipAddresses"]["v6"] = addrs_v6
                    result['nameservers'].append(ns_obj)
                    result['fred_nsset']['nameservers'].append(ns_obj)

        if nonempty(struct.keyset_handle):
            keyset = WHOIS.get_keyset_by_handle(struct.keyset_handle)
            if keyset is not None:
                result["secureDNS"] = {
                    "zoneSigned": True,
                    "delegationSigned": True,
                    "keyData": [],
                }
                if RDAP_SETTINGS.MAX_SIG_LIFE:
                    result['secureDNS']['maxSigLife'] = RDAP_SETTINGS.MAX_SIG_LIFE
                keyset_link = request.build_absolute_uri(reverse('keyset-detail', kwargs={"handle": keyset.handle}))
                result['fred_keyset'] = {
                    "objectClassName": ObjectClassName.KEYSET,
                    "handle": keyset.handle,
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
                        "publicKey": key.public_key,
                    })
                    result["fred_keyset"]['dns_keys'].append({
                        "flags": key.flags,
                        "protocol": key.protocol,
                        "algorithm": key.alg,
                        "publicKey": key.public_key,
                    })

    logging.debug(result)
    return result


def delete_candidate_domain_to_dict(request, handle):
    """Return python dictionary with RDAP data for domain with `deleteCandidate` status."""
    self_link = request.build_absolute_uri(reverse('domain-detail', kwargs={"handle": handle}))

    result = {
        "objectClassName": ObjectClassName.DOMAIN,
        "rdapConformance": ["rdap_level_0", "fred_version_0"],
        "handle": handle,
        "ldhName": handle,
        "links": [
            {
                "value": self_link,
                "rel": "self",
                "href": self_link,
                "type": "application/rdap+json",
            },
        ],
        'status': ["pending delete"],
    }
    if RDAP_SETTINGS.UNIX_WHOIS:
        result['port43'] = RDAP_SETTINGS.UNIX_WHOIS
    add_unicode_name(result, handle)

    logging.debug(result)
    return result
