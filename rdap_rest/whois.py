"""
Wrapper module to whois idl interface
"""
import logging
from datetime import datetime

from django.utils.functional import SimpleLazyObject
from django.conf import settings

from utils.corba import Corba, importIDL
from utils.corbarecoder import u2c, c2u

importIDL(settings.CORBA_IDL_PATH)

_CORBA = Corba(ior=settings.CORBA_NS_HOST_PORT, context_name=settings.CORBA_NS_CONTEXT, export_modules=settings.CORBA_EXPORT_MODULES)
_WHOIS = SimpleLazyObject(lambda: _CORBA.get_object('Whois2', 'Registry.Whois.WhoisIntf'))
_INTERFACE = _CORBA.Registry


def unwrap_datetime(idl_datetime):
    return datetime(idl_datetime.date.year, idl_datetime.date.month, idl_datetime.date.day, idl_datetime.hour, idl_datetime.minute, idl_datetime.second)    

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
        cz_nic_rdap_url_tmp = "http://rdap.nic.cz/entity/%(handle)s"
        self_link = cz_nic_rdap_url_tmp % {"handle": struct.handle}
        cz_nic_unix_whois_url = 'whois.nic.cz'
        
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
          "port43": cz_nic_unix_whois_url,
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


def whois_get_contact_by_handle(handle):
    logging.debug('get_contact_by_handle: %s' % handle)
    return contact_to_dict(c2u(_WHOIS.get_contact_by_handle(u2c(handle))))

