"""Wrapper module to whois idl interface."""
import logging
from datetime import date, datetime

from django.conf import settings
from django.utils import timezone
from pyfco.recoder import CorbaRecoder

from rdap.utils.corba import REGISTRY_MODULE, WHOIS

from .domain import domain_to_dict
from .entity import contact_to_dict
from .keyset import keyset_to_dict
from .nameserver import nameserver_to_dict
from .nsset import nsset_to_dict


class RdapCorbaRecoder(CorbaRecoder):
    """Corba recoder for RDAP."""

    def __init__(self, coding='utf-8'):
        super(RdapCorbaRecoder, self).__init__(coding)
        self.add_recode_function(REGISTRY_MODULE.Date, self._decode_date, self._identity)
        self.add_recode_function(REGISTRY_MODULE.DateTime, self._decode_datetime, self._identity)

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
