"""
Wrapper module to whois idl interface
"""
import logging

from django.conf import settings
from django.utils.functional import SimpleLazyObject

from rdap.utils.corba import Corba, importIDL
from rdap.utils.corbarecoder import u2c, c2u
from .rdap_utils import *


importIDL(settings.CORBA_IDL_ROOT_PATH + '/' + settings.CORBA_IDL_WHOIS_FILENAME)

_CORBA = Corba(ior=settings.CORBA_NS_HOST_PORT, context_name=settings.CORBA_NS_CONTEXT, export_modules=settings.CORBA_EXPORT_MODULES)
_WHOIS = SimpleLazyObject(lambda: _CORBA.get_object('Whois2', 'Registry.Whois.WhoisIntf'))
_INTERFACE = _CORBA.Registry


def nsset_to_dict(struct):
    """
    Transform CORBA nsset struct to python dictionary
    """
    logging.debug(struct)
    
    if struct is None:
        result = None
    else:
        self_link = settings.RDAP_NSSET_URL_TMPL  % {"handle": struct.handle}

        result = {
          "rdapConformance" : ["rdap_level_0", "cznic_version_0"],
          "handle": struct.handle,
          "entities" : 
          [
            {
              "handle" : struct.registrar_handle,
              "roles" : [ "registrar" ]
#              ,
#              "links" : 
#              [
#                {
#                  "value" : settings.RDAP_ENTITY_URL_TMPL  % {"handle": struct.registrar_handle},
#                  "rel" : "self",
#                  "href" : settings.RDAP_ENTITY_URL_TMPL  % {"handle": struct.registrar_handle},
#                  "type" : "application/rdap+json"
#                }
#              ]
            }
          ],
          "status" : struct.statuses,
          "port43" : settings.UNIX_WHOIS_HOST,
          "events" : 
          [
            {
              "eventAction" : "registration",
              "eventDate" : unwrap_datetime(struct.created)
            }
          ],
          "links":[
            {
              "value": self_link,
              "rel":"self",
              "href": self_link,
              "type":"application/rdap+json"
            }
          ],
          "nameServers" : []
        }
        
        for tech_c in struct.tech_contact_handles:
            result['entities'].append({
                "handle" : tech_c,
                "roles" : [ "technical" ],
                "links" : [
                    {
                        "value" : settings.RDAP_ENTITY_URL_TMPL  % {"handle": tech_c},
                        "rel" : "self",
                        "href" : settings.RDAP_ENTITY_URL_TMPL  % {"handle": tech_c},
                        "type" : "application/rdap+json"
                    }
                ]
            })
        
        for ns in struct.nservers:
            ns_json = {
                "handle" : ns.fqdn,
                "ldhName" : ns.fqdn,
                "links" : 
                [
                    {
                        "value" : settings.RDAP_NAMESERVER_URL_TMPL  % {"handle": ns.fqdn},
                        "rel" : "self",
                        "href" : settings.RDAP_NAMESERVER_URL_TMPL  % {"handle": ns.fqdn},
                        "type" : "application/rdap+json"
                    }
                ]
            }
            if ns.ip_addresses:
                addrs_v4 = []
                addrs_v6 = []
                for ip_addr in ns.ip_addresses:
                    if ip_addr.version._v == _CORBA.Registry.Whois.v4._v:
                        addrs_v4.append(ip_addr.address)
                    if ip_addr.version._v == _CORBA.Registry.Whois.v6._v:
                        addrs_v6.append(ip_addr.address)
                ns_json["ipAddresses"] = {}
                if addrs_v4:
                    ns_json["ipAddresses"]["v4"] = addrs_v4
                if addrs_v6:
                    ns_json["ipAddresses"]["v6"] = addrs_v6

            result['nameServers'].append(ns_json)
            
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

    logging.debug(result)
    return result
