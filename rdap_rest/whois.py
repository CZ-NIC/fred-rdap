"""
Wrapper module to whois idl interface
"""
import logging

from django.utils.functional import SimpleLazyObject
from django.conf import settings

from utils.corba import Corba, importIDL
from utils.corbarecoder import u2c, c2u

importIDL(settings.CORBA_IDL_PATH)

_CORBA = Corba(ior=settings.CORBA_NS_HOST_PORT, context_name=settings.CORBA_NS_CONTEXT, export_modules=settings.CORBA_EXPORT_MODULES)
_WHOIS = SimpleLazyObject(lambda: _CORBA.get_object('Whois2', 'Registry.Whois.WhoisIntf'))
_INTERFACE = _CORBA.Registry


def struct_to_dict(struct):
    """
    Transform CORBA struct to python dictionary
    (mainly for testing purpose)
    """
    return dict([(attr, getattr(struct, attr)) for attr in dir(struct) if not attr.startswith('_')])



def whois_get_contact_by_handle(handle):
    logging.debug('whois_get_contact_by_handle: %s' % handle)
    return c2u(_WHOIS.get_contact_by_handle(u2c(handle)))

