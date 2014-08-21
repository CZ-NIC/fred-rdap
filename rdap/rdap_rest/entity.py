"""
Wrapper module to whois idl interface
"""
import logging

from django.conf import settings

from .rdap_utils import unwrap_datetime
from .rdap_utils import nonempty


def contact_to_dict(struct):
    """
    Transform CORBA contact struct to python dictionary
    """
    logging.debug(struct)

    if struct is None:
        result = None
    else:
        self_link = settings.RDAP_ENTITY_URL_TMPL  % {"handle": struct.handle}
        if not "linked" in struct.statuses:
            result = {
                "rdapConformance" : ["rdap_level_0"],
                "handle": struct.handle,
                "links": [
                    {
                        "value": self_link,
                        "rel":"self",
                        "href": self_link,
                        "type":"application/rdap+json",
                    },
                ],
                "port43": settings.UNIX_WHOIS_HOST,
                "remarks":[
                    { "description":[ "Omitting data because contact is not linked to any registry object."] }
                ],
            }
        else:
            vcard = [["version", {}, "text", "4.0"]]

            if nonempty(struct.name):
                vcard.append(["fn", {}, "text", struct.name])
            if nonempty(struct.organization):
                vcard.append(["org", {}, "text", struct.organization])
            if nonempty(struct.address):
                vcard.append(
                    [
                        "adr",
                        {"type": ""},
                        "text",
                        [
                          '',  # P. O. BOX
                          struct.address.street1,
                          struct.address.street2,
                          struct.address.street3,
                          struct.address.city,
                          struct.address.stateorprovince,
                          struct.address.postalcode,
                          struct.address.country_code,
                        ]
                    ]
                )
            if nonempty(struct.phone):
                vcard.append(
                    ["tel", {"type": ["voice"]}, "uri", "tel:%s" % struct.phone]
                )
            if nonempty(struct.fax):
                vcard.append(
                    ["tel", {"type": ["fax"]}, "uri", "tel:%s" % struct.fax]
                )
            if nonempty(struct.email):
                vcard.append(
                    ["email", {"type": ""}, "text", struct.email]
                )

            result = {
                "rdapConformance" : ["rdap_level_0"],
                "handle": struct.handle,
                "vcardArray": ["vcard", vcard],
                "links": [
                    {
                        "value": self_link,
                        "rel":"self",
                        "href": self_link,
                        "type":"application/rdap+json",
                    },
                ],
                "port43": settings.UNIX_WHOIS_HOST,
                "events": [
                    {
                        "eventAction": "registration",
                        "eventDate": unwrap_datetime(struct.created),
                        "eventActor": struct.creating_registrar_handle,
                    }
                ],
                "entities": [
                    {
                        "handle": struct.sponsoring_registrar_handle,
                        "roles": ["registrar"],
                    },
                ],
            }
            if struct.statuses:
                result["status"] = struct.statuses
            if nonempty(struct.changed):
                result['events'].append({
                    "eventAction": 'last changed',
                    "eventDate": unwrap_datetime(struct.changed),
                })
            if nonempty(struct.last_transfer):
                result['events'].append({
                    "eventAction": 'transfer',
                    "eventDate": unwrap_datetime(struct.last_transfer),
                })

    logging.debug(result)
    return result
