"""Wrapper module to whois idl interface."""
from __future__ import unicode_literals

import logging
from urlparse import urljoin

from django.conf import settings
from django.urls import reverse

from .rdap_utils import ObjectClassName, disclosable_nonempty, nonempty, rdap_status_mapping, to_rfc3339


def contact_to_dict(struct):
    """Transform CORBA contact struct to python dictionary."""
    logging.debug(struct)

    if struct is None:
        result = None
    else:
        self_link = urljoin(settings.RDAP_ROOT_URL, reverse('entity-detail', kwargs={"handle": struct.handle}))
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
                "port43": settings.UNIX_WHOIS_HOST,
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
                "port43": settings.UNIX_WHOIS_HOST,
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

    logging.debug(result)
    return result
