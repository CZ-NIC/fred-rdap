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
from typing import Any, Dict, List, cast

from django.http import HttpRequest
from django.urls import reverse
from regal import Contact, ObjectEvents

from rdap.constants import ObjectStatus, Publish
from rdap.settings import RDAP_SETTINGS
from rdap.utils.corba import CONTACT_CLIENT

from .rdap_utils import ObjectClassName, rdap_status_mapping, to_rfc3339


def contact_to_dict(contact: Contact, request: HttpRequest) -> Dict[str, Any]:
    """Transform contact to python dictionary."""
    logging.debug(contact)
    events = cast(ObjectEvents, contact.events)

    self_link = request.build_absolute_uri(reverse('entity-detail', kwargs={"handle": contact.contact_handle}))
    statuses = CONTACT_CLIENT.get_contact_state(contact.contact_id)
    if not statuses.get(ObjectStatus.LINKED, False):
        result: Dict[str, Any] = {
            "rdapConformance": ["rdap_level_0"],
            "objectClassName": ObjectClassName.ENTITY,
            "handle": contact.contact_handle,
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
                    "handle": contact.sponsoring_registrar,
                    "roles": ["registrar"],
                },
            ],
            "remarks": [
                {"description": ["Omitting data because contact is not linked to any registry object."]}
            ],
        }
    else:
        vcard: List[List[Any]] = [["version", {}, "text", "4.0"]]

        if contact.name and contact.publish.get(Publish.NAME, False):
            vcard.append(["fn", {}, "text", contact.name])
        if contact.organization and contact.publish.get(Publish.ORGANIZATION, False):
            vcard.append(["org", {}, "text", contact.organization])
        if contact.place and contact.publish.get(Publish.PLACE, False):
            streets = (list(contact.place.street) + ['', '', ''])[:3]
            address = (
                ['']  # P. O. BOX
                + streets
                + [contact.place.city, contact.place.state_or_province, contact.place.postal_code,
                   contact.place.country_code])
            vcard.append(["adr", {"type": ""}, "text", address])
        if contact.telephone and contact.publish.get(Publish.TELEPHONE, False):
            vcard.append(
                ["tel", {"type": ["voice"]}, "uri", "tel:%s" % contact.telephone]
            )
        if contact.fax and contact.publish.get(Publish.FAX, False):
            vcard.append(
                ["tel", {"type": ["fax"]}, "uri", "tel:%s" % contact.fax]
            )
        if contact.emails and contact.publish.get(Publish.EMAILS, False):
            for email in contact.emails:
                vcard.append(["email", {"type": ""}, "text", email])

        result = {
            "objectClassName": ObjectClassName.ENTITY,
            "rdapConformance": ["rdap_level_0"],
            "handle": contact.contact_handle,
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
                    "eventDate": to_rfc3339(cast(datetime, events.registered.timestamp)),
                    "eventActor": events.registered.registrar_handle,
                }
            ],
            "entities": [
                {
                    "objectClassName": ObjectClassName.ENTITY,
                    "handle": contact.sponsoring_registrar,
                    "roles": ["registrar"],
                },
            ],
        }
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
    if RDAP_SETTINGS.UNIX_WHOIS:
        result['port43'] = RDAP_SETTINGS.UNIX_WHOIS

    logging.debug(result)
    return result
