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

from rdap.settings import RDAP_SETTINGS

from .rdap_utils import ObjectClassName, nonempty, rdap_status_mapping, to_rfc3339


def keyset_to_dict(request, struct):
    """Transform CORBA keyset struct to python dictionary."""
    logging.debug(struct)

    if struct is None:
        result = None
    else:
        self_link = request.build_absolute_uri(reverse('keyset-detail', kwargs={"handle": struct.handle}))

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
        if RDAP_SETTINGS.UNIX_WHOIS:
            result['port43'] = RDAP_SETTINGS.UNIX_WHOIS

        status = rdap_status_mapping(struct.statuses)
        if status:
            result["status"] = status

        for tech_c in struct.tech_contact_handles:
            tech_link = request.build_absolute_uri(reverse('entity-detail', kwargs={"handle": tech_c}))
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
