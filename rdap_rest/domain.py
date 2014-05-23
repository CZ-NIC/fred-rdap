"""
Wrapper module to whois idl interface
"""
import logging
from django.conf import settings
from rdap_utils import *

def domain_to_dict(struct):
    """
    Transform CORBA struct to python dictionary
    """
    logging.debug(struct)   
    
    result = {
      "rdapConformance" : ["rdap_level_0"]
    }    
    
    logging.debug(result)
    return result
