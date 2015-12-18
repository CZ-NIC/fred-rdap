"""
Wrapper module to whois idl interface
"""
import logging

from django.conf import settings
from django.utils.functional import SimpleLazyObject

from rdap.utils.corba import Corba, importIDL
from rdap.utils.corbarecoder import u2c, c2u
from .domain import domain_to_dict
from .entity import contact_to_dict
from .keyset import keyset_to_dict
from .nameserver import nameserver_to_dict
from .nsset import nsset_to_dict


importIDL(settings.CORBA_IDL_ROOT_PATH + '/' + settings.CORBA_IDL_WHOIS_FILENAME)

_CORBA = Corba(ior=settings.CORBA_NS_HOST_PORT, context_name=settings.CORBA_NS_CONTEXT,
               export_modules=settings.CORBA_EXPORT_MODULES)
_WHOIS = SimpleLazyObject(lambda: _CORBA.get_object('Whois2', 'Registry.Whois.WhoisIntf'))
_INTERFACE = _CORBA.Registry


class NotFoundError(Exception):
    pass


class InvalidHandleError(Exception):
    pass



def get_contact_by_handle(handle):
    logging.debug('get_contact_by_handle: %s', handle)
    try:
        return contact_to_dict(c2u(_WHOIS.get_contact_by_handle(u2c(handle))))
    except _INTERFACE.Whois.OBJECT_NOT_FOUND, e:
        raise NotFoundError()
    except _INTERFACE.Whois.INVALID_HANDLE, e:
        raise InvalidHandleError()


def get_domain_by_handle(handle):
    logging.debug('get_domain_by_handle: %s', handle)
    try:
        return domain_to_dict(c2u(_WHOIS.get_domain_by_handle(u2c(handle))))
    except (_INTERFACE.Whois.OBJECT_NOT_FOUND, _INTERFACE.Whois.TOO_MANY_LABELS, _INTERFACE.Whois.UNMANAGED_ZONE), e:
        raise NotFoundError()
    except _INTERFACE.Whois.INVALID_LABEL, e:
        raise InvalidHandleError()


def get_nameserver_by_handle(handle):
    logging.debug('get_nameserver_by_handle: %s', handle)
    try:
        return nameserver_to_dict(c2u(_WHOIS.get_nameserver_by_fqdn(u2c(handle))))
    except _INTERFACE.Whois.OBJECT_NOT_FOUND, e:
        raise NotFoundError()
    except _INTERFACE.Whois.INVALID_HANDLE, e:
        raise InvalidHandleError()


def get_nsset_by_handle(handle):
    logging.debug('get_nsset_by_handle: %s', handle)
    try:
        return nsset_to_dict(c2u(_WHOIS.get_nsset_by_handle(u2c(handle))))
    except _INTERFACE.Whois.OBJECT_NOT_FOUND, e:
        raise NotFoundError()
    except _INTERFACE.Whois.INVALID_HANDLE, e:
        raise InvalidHandleError()


def get_keyset_by_handle(handle):
    logging.debug('get_keyset_by_handle: %s', handle)
    try:
        return keyset_to_dict(c2u(_WHOIS.get_keyset_by_handle(u2c(handle))))
    except _INTERFACE.Whois.OBJECT_NOT_FOUND, e:
        raise NotFoundError()
    except _INTERFACE.Whois.INVALID_HANDLE, e:
        raise InvalidHandleError()
