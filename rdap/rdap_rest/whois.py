"""Wrapper module to whois idl interface."""
from __future__ import unicode_literals

import logging

from fred_idl.Registry.Whois import INVALID_HANDLE, INVALID_LABEL, OBJECT_DELETE_CANDIDATE, OBJECT_NOT_FOUND, \
    TOO_MANY_LABELS, UNMANAGED_ZONE

from rdap.exceptions import InvalidHandleError, NotFoundError
from rdap.utils.corba import WHOIS

from .domain import delete_candidate_domain_to_dict, domain_to_dict
from .entity import contact_to_dict
from .keyset import keyset_to_dict
from .nameserver import nameserver_to_dict
from .nsset import nsset_to_dict


def get_contact_by_handle(handle):
    logging.debug('get_contact_by_handle: %s', handle)
    try:
        return contact_to_dict(WHOIS.get_contact_by_handle(handle))
    except OBJECT_NOT_FOUND:
        raise NotFoundError()
    except INVALID_HANDLE:
        raise InvalidHandleError()


def get_domain_by_handle(handle):
    logging.debug('get_domain_by_handle: %s', handle)
    try:
        return domain_to_dict(WHOIS.get_domain_by_handle(handle))
    except OBJECT_DELETE_CANDIDATE:
        return delete_candidate_domain_to_dict(handle)
    except (OBJECT_NOT_FOUND, TOO_MANY_LABELS, UNMANAGED_ZONE):
        raise NotFoundError()
    except INVALID_LABEL:
        raise InvalidHandleError()


def get_nameserver_by_handle(handle):
    logging.debug('get_nameserver_by_handle: %s', handle)
    try:
        return nameserver_to_dict(WHOIS.get_nameserver_by_fqdn(handle))
    except OBJECT_NOT_FOUND:
        raise NotFoundError()
    except INVALID_HANDLE:
        raise InvalidHandleError()


def get_nsset_by_handle(handle):
    logging.debug('get_nsset_by_handle: %s', handle)
    try:
        return nsset_to_dict(WHOIS.get_nsset_by_handle(handle))
    except OBJECT_NOT_FOUND:
        raise NotFoundError()
    except INVALID_HANDLE:
        raise InvalidHandleError()


def get_keyset_by_handle(handle):
    logging.debug('get_keyset_by_handle: %s', handle)
    try:
        return keyset_to_dict(WHOIS.get_keyset_by_handle(handle))
    except OBJECT_NOT_FOUND:
        raise NotFoundError()
    except INVALID_HANDLE:
        raise InvalidHandleError()
