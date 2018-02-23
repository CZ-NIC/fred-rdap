#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date, datetime

from django.conf import settings
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from fred_idl.ccReg import DateTimeType, DateType, Logger
from fred_idl.Registry import Date, DateTime, Whois
from pyfco import CorbaClient, CorbaClientProxy, CorbaNameServiceClient, CorbaRecoder

_CORBA = CorbaNameServiceClient(host_port=settings.CORBA_NS_HOST_PORT, context_name=settings.CORBA_NS_CONTEXT)
_WHOIS = SimpleLazyObject(lambda: _CORBA.get_object('Whois2', Whois.WhoisIntf))
_LOGGER = SimpleLazyObject(lambda: _CORBA.get_object('Logger', Logger))


class RdapCorbaRecoder(CorbaRecoder):
    """Corba recoder for RDAP."""

    def __init__(self, coding='utf-8'):
        super(RdapCorbaRecoder, self).__init__(coding)
        self.add_recode_function(DateType, self._decode_date, self._identity)
        self.add_recode_function(DateTimeType, self._decode_datetime, self._identity)
        self.add_recode_function(Date, self._decode_date, self._identity)
        self.add_recode_function(DateTime, self._decode_datetime, self._identity)

    def _decode_date(self, value):
        # Delete candidates returns dates with zeros, see #20984.
        # TODO: Remove once #16223 is resolved.
        if value.year == 0 and value.month == 0 and value.day == 0:
            return None
        return date(value.year, value.month, value.day)

    def _decode_datetime(self, value):
        # Delete candidates returns dates with zeros, see #20984.
        # TODO: Remove once #16223 is resolved.
        if value.date.year == 0 and value.date.month == 0 and value.date.day == 0:
            return None
        result = datetime(value.date.year, value.date.month, value.date.day, value.hour, value.minute, value.second)
        result = timezone.make_aware(result, timezone.utc)
        # If time zones are disabled, change the time to the default timezone and remove the time zone.
        if not settings.USE_TZ:
            result = timezone.make_naive(result, timezone.get_default_timezone())
        return result


WHOIS = CorbaClientProxy(CorbaClient(_WHOIS, RdapCorbaRecoder(), Whois.INTERNAL_SERVER_ERROR))
LOGGER = CorbaClientProxy(CorbaClient(_LOGGER, CorbaRecoder('utf-8'), Logger.INTERNAL_SERVER_ERROR))
