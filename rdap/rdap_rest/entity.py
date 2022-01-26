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
from typing import Any, Dict, Optional

from django.http import HttpRequest
from django.urls import reverse
from fred_idl.Registry.Whois import Contact

from rdap.settings import RDAP_SETTINGS

from .rdap_utils import ObjectClassName, disclosable_nonempty, nonempty, rdap_status_mapping, to_rfc3339


def contact_to_dict(request: HttpRequest, struct: Contact) -> Optional[Dict[str, Any]]:
    """Transform CORBA contact struct to python dictionary."""
    logging.debug(struct)

    if struct is None:
        result = None
    else:
        self_link = request.build_absolute_uri(reverse('entity-detail', kwargs={"handle": struct.handle}))
        if "linked" not in struct.statuses:
            result = {
                "rdapConformance": ["rdap_level_0"],
                "objectClassName": ObjectClassName.ENTITY,
                "handle": struct.handle,
                "links": [
                    {
                        "value": self_link,
                        "rel": "self",
                        "href": self_link,
                        "type": "application/rdap+json",
                    },
                ],
                "entities": [
                    {
                        "objectClassName": ObjectClassName.ENTITY,
                        "handle": struct.sponsoring_registrar_handle,
                        "roles": ["registrar"],
                    },
                ],
                "remarks": [
                    {"description": ["Omitting data because contact is not linked to any registry object."]}
                ],
            }
        else:
            vcard = [["version", {}, "text", "4.0"]]

            if disclosable_nonempty(struct.name):
                vcard.append(["fn", {}, "text", struct.name.value])
            if disclosable_nonempty(struct.organization):
                vcard.append(["org", {}, "text", struct.organization.value])
            if disclosable_nonempty(struct.address):
                address = struct.address.value
                vcard.append(
                    [
                        "adr",
                        {"type": ""},
                        "text",
                        [
                            '',  # P. O. BOX
                            address.street1,
                            address.street2,
                            address.street3,
                            address.city,
                            address.stateorprovince,
                            address.postalcode,
                            address.country_code,
                        ]
                    ]
                )
            if disclosable_nonempty(struct.phone):
                vcard.append(
                    ["tel", {"type": ["voice"]}, "uri", "tel:%s" % struct.phone.value]
                )
            if disclosable_nonempty(struct.fax):
                vcard.append(
                    ["tel", {"type": ["fax"]}, "uri", "tel:%s" % struct.fax.value]
                )
            if disclosable_nonempty(struct.email):
                vcard.append(
                    ["email", {"type": ""}, "text", struct.email.value]
                )

            result = {
                "objectClassName": ObjectClassName.ENTITY,
                "rdapConformance": ["rdap_level_0"],
                "handle": struct.handle,
                "vcardArray": ["vcard", vcard],
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
                        "eventDate": to_rfc3339(struct.created),
                        "eventActor": struct.creating_registrar_handle,
                    }
                ],
                "entities": [
                    {
                        "objectClassName": ObjectClassName.ENTITY,
                        "handle": struct.sponsoring_registrar_handle,
                        "roles": ["registrar"],
                    },
                ],
            }
            status = rdap_status_mapping(struct.statuses)
            if status:
                result["status"] = status
            if nonempty(struct.changed):
                result['events'].append({
                    "eventAction": 'last changed',
                    "eventDate": to_rfc3339(struct.changed),
                })
            if nonempty(struct.last_transfer):
                result['events'].append({
                    "eventAction": 'transfer',
                    "eventDate": to_rfc3339(struct.last_transfer),
                })
        if RDAP_SETTINGS.UNIX_WHOIS:
            result['port43'] = RDAP_SETTINGS.UNIX_WHOIS

    logging.debug(result)
    return result
