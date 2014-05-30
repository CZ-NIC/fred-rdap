"""
Wrapper module to whois idl interface
"""
import logging
from django.conf import settings
from rdap_utils import *

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
              "eventDate" : "1990-12-31T23:59:60Z"
            },
            {
              "eventAction" : "last changed",
              "eventDate" : "1991-12-31T23:59:60Z",
              "eventActor" : "joe@example.com"
            },
            {
              "eventAction" : "transfer",
              "eventDate" : "1991-12-31T23:59:60Z",
              "eventActor" : "joe@example.com"
            },
            {
              "eventAction" : "expiration",
              "eventDate" : "2016-12-31T23:59:60Z",
              "eventActor" : "joe@example.com"
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
          ]
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
    
    logging.debug(result)
    return result
