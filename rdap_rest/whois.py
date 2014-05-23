"""
Wrapper module to whois idl interface
"""
import logging
from datetime import datetime

from django.utils.functional import SimpleLazyObject
from django.conf import settings

from utils.corba import Corba, importIDL
from utils.corbarecoder import u2c, c2u

import entity
import domain

importIDL(settings.CORBA_IDL_PATH)

_CORBA = Corba(ior=settings.CORBA_NS_HOST_PORT, context_name=settings.CORBA_NS_CONTEXT, export_modules=settings.CORBA_EXPORT_MODULES)
_WHOIS = SimpleLazyObject(lambda: _CORBA.get_object('Whois2', 'Registry.Whois.WhoisIntf'))
_INTERFACE = _CORBA.Registry

def whois_get_contact_by_handle(handle):
    logging.debug('get_contact_by_handle: %s' % handle)
    return entity.contact_to_dict(c2u(_WHOIS.get_contact_by_handle(u2c(handle))))

def whois_get_domain_by_handle(handle):
    logging.debug('get_contact_by_handle: %s' % handle)
    return domain.domain_to_dict(c2u(_WHOIS.get_contact_by_handle(u2c(handle))))
