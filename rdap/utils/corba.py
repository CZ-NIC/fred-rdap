#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from fred_idl.ccReg import Logger
from fred_idl.Registry import IsoDate, IsoDateTime, Whois
from pyfco import CorbaClient, CorbaClientProxy, CorbaNameServiceClient, CorbaRecoder
from pyfco.recoder import decode_iso_date, decode_iso_datetime

_CORBA = CorbaNameServiceClient(host_port=settings.CORBA_NS_HOST_PORT, context_name=settings.CORBA_NS_CONTEXT)
_WHOIS = SimpleLazyObject(lambda: _CORBA.get_object('Whois2', Whois.WhoisIntf))
_LOGGER = SimpleLazyObject(lambda: _CORBA.get_object('Logger', Logger))


class RdapCorbaRecoder(CorbaRecoder):
    """Corba recoder for RDAP."""

    def __init__(self, coding='utf-8'):
        super(RdapCorbaRecoder, self).__init__(coding)
        self.add_recode_function(IsoDate, decode_iso_date, self._identity)
        self.add_recode_function(IsoDateTime, self._decode_iso_datetime, self._identity)

    def _decode_iso_datetime(self, value):
        """Decode `IsoDateTime` struct to datetime object with respect to the timezone settings."""
        result = decode_iso_datetime(value)
        if not settings.USE_TZ:
            result = timezone.make_naive(result, timezone.get_default_timezone())
        return result


WHOIS = CorbaClientProxy(CorbaClient(_WHOIS, RdapCorbaRecoder(), Whois.INTERNAL_SERVER_ERROR))
LOGGER = CorbaClientProxy(CorbaClient(_LOGGER, CorbaRecoder('utf-8'), Logger.INTERNAL_SERVER_ERROR))
