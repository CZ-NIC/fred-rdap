"""Wrapper module to whois idl interface."""
import logging

from rdap.exceptions import InvalidHandleError, NotFoundError
from rdap.utils.corba import RECODER, REGISTRY_MODULE, WHOIS

from .domain import domain_to_dict
from .entity import contact_to_dict
from .keyset import keyset_to_dict
from .nameserver import nameserver_to_dict
from .nsset import nsset_to_dict


def get_contact_by_handle(handle):
    logging.debug('get_contact_by_handle: %s', handle)
    try:
        return contact_to_dict(RECODER.decode(WHOIS.get_contact_by_handle(RECODER.encode(handle))))
    except REGISTRY_MODULE.Whois.OBJECT_NOT_FOUND:
        raise NotFoundError()
    except REGISTRY_MODULE.Whois.INVALID_HANDLE:
        raise InvalidHandleError()


def get_domain_by_handle(handle):
    logging.debug('get_domain_by_handle: %s', handle)
    try:
        return domain_to_dict(RECODER.decode(WHOIS.get_domain_by_handle(RECODER.encode(handle))))
    except (REGISTRY_MODULE.Whois.OBJECT_NOT_FOUND, REGISTRY_MODULE.Whois.TOO_MANY_LABELS,
            REGISTRY_MODULE.Whois.UNMANAGED_ZONE):
        raise NotFoundError()
    except REGISTRY_MODULE.Whois.INVALID_LABEL:
        raise InvalidHandleError()


def get_nameserver_by_handle(handle):
    logging.debug('get_nameserver_by_handle: %s', handle)
    try:
        return nameserver_to_dict(RECODER.decode(WHOIS.get_nameserver_by_fqdn(RECODER.encode(handle))))
    except REGISTRY_MODULE.Whois.OBJECT_NOT_FOUND:
        raise NotFoundError()
    except REGISTRY_MODULE.Whois.INVALID_HANDLE:
        raise InvalidHandleError()


def get_nsset_by_handle(handle):
    logging.debug('get_nsset_by_handle: %s', handle)
    try:
        return nsset_to_dict(RECODER.decode(WHOIS.get_nsset_by_handle(RECODER.encode(handle))))
    except REGISTRY_MODULE.Whois.OBJECT_NOT_FOUND:
        raise NotFoundError()
    except REGISTRY_MODULE.Whois.INVALID_HANDLE:
        raise InvalidHandleError()


def get_keyset_by_handle(handle):
    logging.debug('get_keyset_by_handle: %s', handle)
    try:
        return keyset_to_dict(RECODER.decode(WHOIS.get_keyset_by_handle(RECODER.encode(handle))))
    except REGISTRY_MODULE.Whois.OBJECT_NOT_FOUND:
        raise NotFoundError()
    except REGISTRY_MODULE.Whois.INVALID_HANDLE:
        raise InvalidHandleError()
