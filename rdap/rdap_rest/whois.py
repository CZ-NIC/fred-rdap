"""Wrapper module to whois idl interface."""
import logging
from datetime import date, datetime

from django.conf import settings
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from pyfco.recoder import CorbaRecoder

from rdap.utils.corba import Corba, importIDL

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


class RdapCorbaRecoder(CorbaRecoder):
    """Corba recoder for RDAP."""

    def __init__(self, coding='utf-8'):
        super(RdapCorbaRecoder, self).__init__(coding)
        self.add_recode_function(_INTERFACE.Date, self._decode_date, self._identity)
        self.add_recode_function(_INTERFACE.DateTime, self._decode_datetime, self._identity)

    def _decode_date(self, value):
        return date(value.year, value.month, value.day)

    def _decode_datetime(self, value):
        result = datetime(value.date.year, value.date.month, value.date.day, value.hour, value.minute, value.second)
        result = timezone.make_aware(result, timezone.utc)
        # If time zones are disabled, change the time to the default timezone and remove the time zone.
        if not settings.USE_TZ:
            result = timezone.make_naive(result, timezone.get_default_timezone())
        return result


RECODER = RdapCorbaRecoder()


class NotFoundError(Exception):
    """Represents error when requested object is not found."""


class InvalidHandleError(Exception):
    """Requested object identifier is not valid (bad format)."""


def get_contact_by_handle(handle):
    logging.debug('get_contact_by_handle: %s', handle)
    try:
        return contact_to_dict(RECODER.decode(_WHOIS.get_contact_by_handle(RECODER.encode(handle))))
    except _INTERFACE.Whois.OBJECT_NOT_FOUND:
        raise NotFoundError()
    except _INTERFACE.Whois.INVALID_HANDLE:
        raise InvalidHandleError()


def get_domain_by_handle(handle):
    logging.debug('get_domain_by_handle: %s', handle)
    try:
        return domain_to_dict(RECODER.decode(_WHOIS.get_domain_by_handle(RECODER.encode(handle))))
    except (_INTERFACE.Whois.OBJECT_NOT_FOUND, _INTERFACE.Whois.TOO_MANY_LABELS, _INTERFACE.Whois.UNMANAGED_ZONE):
        raise NotFoundError()
    except _INTERFACE.Whois.INVALID_LABEL:
        raise InvalidHandleError()


def get_nameserver_by_handle(handle):
    logging.debug('get_nameserver_by_handle: %s', handle)
    try:
        return nameserver_to_dict(RECODER.decode(_WHOIS.get_nameserver_by_fqdn(RECODER.encode(handle))))
    except _INTERFACE.Whois.OBJECT_NOT_FOUND:
        raise NotFoundError()
    except _INTERFACE.Whois.INVALID_HANDLE:
        raise InvalidHandleError()


def get_nsset_by_handle(handle):
    logging.debug('get_nsset_by_handle: %s', handle)
    try:
        return nsset_to_dict(RECODER.decode(_WHOIS.get_nsset_by_handle(RECODER.encode(handle))))
    except _INTERFACE.Whois.OBJECT_NOT_FOUND:
        raise NotFoundError()
    except _INTERFACE.Whois.INVALID_HANDLE:
        raise InvalidHandleError()


def get_keyset_by_handle(handle):
    logging.debug('get_keyset_by_handle: %s', handle)
    try:
        return keyset_to_dict(RECODER.decode(_WHOIS.get_keyset_by_handle(RECODER.encode(handle))))
    except _INTERFACE.Whois.OBJECT_NOT_FOUND:
        raise NotFoundError()
    except _INTERFACE.Whois.INVALID_HANDLE:
        raise InvalidHandleError()
