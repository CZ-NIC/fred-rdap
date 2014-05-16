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


def contact_to_dict(struct):
    """
    Transform CORBA struct to python dictionary
    """
    logging.debug(struct)

    cz_nic_rdap_url = 'rdap.nic.cz'
    cz_nic_unix_whois_url = 'whois.nic.cz'

    result = {
      "handle": struct.handle,
      "vcardArray":[
        "vcard",
        [
          ["version", {}, "text", "4.0"],
          ["fn", {}, "text", struct.name],
          ["org", {}, "text", struct.organization],
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
          ],
          ["tel",
            { "type":["official"] },
            "uri", "tel:"+ struct.phone
          ],
          ["email",
            { "type":"official" },
            "text", struct.email
          ],
        ]
      ],
      "status": struct.statuses,               #? tady by asi casem mohl byt preklad
      "links":[
        {
          "value":"http://"+ cz_nic_rdap_url +"/entity/"+ struct.handle,
          "rel":"self",
          "href":"http://"+ cz_nic_rdap_url +"/entity/"+ struct.handle,
          "type":"application/rdap+json"
        }
      ],
      "port43": cz_nic_unix_whois_url,
      "events":[
        {
          "eventAction": "created",
          "eventDate": datetime(struct.created.date.year, struct.created.date.month, struct.created.date.day, struct.created.hour, struct.created.minute, struct.created.second),
          "eventActor": struct.creating_registrar_handle
        }
      ]
    }
    if struct.changed is not None:
        result['events'].append({
            "eventAction": 'last_update',
            "eventDate": datetime(struct.changed.date.year, struct.changed.date.month, struct.changed.date.day, struct.changed.hour, struct.changed.minute, struct.changed.second)
        })
    if struct.last_transfer is not None:
        result['events'].append({
            "eventAction": 'last_transfer',
            "eventDate": datetime(struct.last_transfer.date.year, struct.last_transfer.date.month, struct.last_transfer.date.day, struct.last_transfer.hour, struct.last_transfer.minute, struct.last_transfer.second)
        })

    logging.debug(result)
    return result


def whois_get_contact_by_handle(handle):
    logging.debug('get_contact_by_handle: %s' % handle)
    return contact_to_dict(c2u(_WHOIS.get_contact_by_handle(u2c(handle))))

