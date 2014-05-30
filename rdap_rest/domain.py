"""
Wrapper module to whois idl interface
"""
import logging
from django.conf import settings
from rdap_utils import *

from django.utils.functional import SimpleLazyObject

from utils.corba import Corba, importIDL
from utils.corbarecoder import u2c, c2u

importIDL(settings.CORBA_IDL_PATH)

_CORBA = Corba(ior=settings.CORBA_NS_HOST_PORT, context_name=settings.CORBA_NS_CONTEXT, export_modules=settings.CORBA_EXPORT_MODULES)
_WHOIS = SimpleLazyObject(lambda: _CORBA.get_object('Whois2', 'Registry.Whois.WhoisIntf'))
_INTERFACE = _CORBA.Registry

def domain_to_dict(struct):
    """
    Transform CORBA domain struct to python dictionary
    """
    logging.debug(struct)   
    
    if struct is None:
        result = {
          "rdapConformance" : ["rdap_level_0"]
        }    
    else:
        self_link = settings.RDAP_DOMAIN_URL_TMPL  % {"handle": struct.handle}
        
        result = {
          "rdapConformance" : ["rdap_level_0"],
          "handle" : struct.handle,
          "ldhName" : struct.handle,
          "unicodeName" : struct.handle,
          "status" : struct.statuses,
          "links" : 
          [
            {
              "value": self_link,
              "rel" : "self",
              "href" : self_link,
              "type" : "application/rdap+json"
            }
          ],
          "port43" : settings.UNIX_WHOIS_HOST,
          "events" : 
          [
            {
              "eventAction" : "registration",
              "eventDate" : unwrap_datetime(struct.registered)
            },
            {
              "eventAction" : "expiration",
              "eventDate" : unwrap_date(struct.expire)
            }
          ],
          "entities" : 
          [
            {
              "handle" : struct.registrant_handle,
              "roles" : [ "registrant" ],
              "links" : 
              [
                {
                  "value" : settings.RDAP_ENTITY_URL_TMPL  % {"handle": struct.registrant_handle},
                  "rel" : "self",
                  "href" : settings.RDAP_ENTITY_URL_TMPL  % {"handle": struct.registrant_handle},
                  "type" : "application/rdap+json"
                }
              ]
            },   
          ],
          "nameServers" : []
        }
        
        for admin_contact in struct.admin_contact_handles:
            result['entities'].append(
                {
                    "handle" : admin_contact,
                    "roles" : [ "technical" ],
                    "links" : 
                    [{
                        "value" : settings.RDAP_ENTITY_URL_TMPL  % {"handle": admin_contact},
                        "rel" : "self",
                        "href" : settings.RDAP_ENTITY_URL_TMPL  % {"handle": admin_contact},
                        "type" : "application/rdap+json"
                    }]
                }
            )
        if struct.changed is not None:
            result['events'].append({
                "eventAction" : "last changed",
                "eventDate": unwrap_datetime(struct.changed)
            })
        if struct.last_transfer is not None:
            result['events'].append({
                "eventAction" : "transfer",
                "eventDate": unwrap_datetime(struct.last_transfer)
            })
        if struct.validated_to is not None:
            result['events'].append({
                "eventAction" : "enum validation expiration",
                "eventDate": unwrap_date(struct.validated_to)
            })
        if struct.nsset_handle != "":
            nsset = c2u(_WHOIS.get_nsset_by_handle(u2c(struct.nsset_handle)))
            if nsset is not None:
                for ns_fqdn in nsset.nservers:
                    result['nameServers'].append({
                        "handle" : ns_fqdn,
                        "ldhName" : ns_fqdn,
                        "links" : 
                        [
                            {
                                "value" : settings.RDAP_NAMESERVER_URL_TMPL  % {"handle": ns_fqdn},
                                "rel" : "self",
                                "href" : settings.RDAP_NAMESERVER_URL_TMPL  % {"handle": ns_fqdn},
                                "type" : "application/rdap+json"
                            }
                        ]
                    })
    
    logging.debug(result)
    return result
