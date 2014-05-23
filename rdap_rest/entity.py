"""
Wrapper module to whois idl interface
"""
import logging
from django.conf import settings
from rdap_utils import *

def contact_to_dict(struct):
    """
    Transform CORBA struct to python dictionary
    """
    logging.debug(struct)
    
    if struct is None:
        result = {
          "rdapConformance" : ["rdap_level_0"]
        }    
    else:
        cz_nic_rdap_url_tmp = "%(rdap_root_url)s/entity/%(handle)s"
        self_link = cz_nic_rdap_url_tmp % {"rdap_root_url": settings.RDAP_ROOT_URL, "handle": struct.handle}
        
        vcard = [ ["version", {}, "text", "4.0"] ]
        
        if struct.name is not None:
            vcard.append( ["fn", {}, "text", struct.name] )
        if struct.organization is not None:
            vcard.append( ["org", {}, "text", struct.organization] )
        if struct.address is not None:
            vcard.append(
                ["adr",
                    { "type":"official" },
                    "text",
                    [
                      '', # P. O. BOX
                      struct.address.street1,
                      struct.address.street2,
                      struct.address.street3,
                      struct.address.city,
                      struct.address.stateorprovince,
                      struct.address.postalcode,
                      struct.address.country_code
                    ]
                ]
            )
        if struct.phone is not None:
            vcard.append(
                ["tel", { "type":["official"] },
                "uri", "tel:"+ struct.phone
                ]
            )
        if struct.email is not None:
            vcard.append(
                ["email",
                { "type":"official" },
                "text", struct.email
                ]
            )

        result = {
          "rdapConformance" : ["rdap_level_0"],
          "handle": struct.handle,
          "vcardArray":[ "vcard", vcard ],
          "status": struct.statuses,
          "links":[
            {
              "value": self_link,
              "rel":"self",
              "href": self_link,
              "type":"application/rdap+json"
            }
          ],
          "port43": settings.UNIX_WHOIS_HOST,
          "events":[
            {
              "eventAction": "created",
              "eventDate": unwrap_datetime(struct.created),
              "eventActor": struct.creating_registrar_handle
            }
          ]
        }
        if struct.changed is not None:
            result['events'].append({
                "eventAction": 'last_update',
                "eventDate": unwrap_datetime(struct.changed)
            })
        if struct.last_transfer is not None:
            result['events'].append({
                "eventAction": 'last_transfer',
                "eventDate": unwrap_datetime(struct.last_transfer)
            })

    logging.debug(result)
    return result
