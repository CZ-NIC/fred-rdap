#!/usr/bin/python
# -*- coding: utf-8 -*-
import os.path
from datetime import date, datetime

import omniORB
from django.conf import settings
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from fred_idl.Registry import Date, DateTime, Whois
from pyfco import CorbaClient, CorbaClientProxy, CorbaNameServiceClient, CorbaRecoder


def _get_ccreg_module():
    """Return `ccReg` module."""
    try:
        import ccReg
    except ImportError:
        ccReg = None

    if not hasattr(ccReg, 'Logger'):
        omniORB.importIDL(os.path.join(settings.CORBA_IDL_ROOT_PATH, settings.CORBA_IDL_LOGGER_FILENAME))
        import ccReg
    return ccReg


CCREG_MODULE = SimpleLazyObject(_get_ccreg_module)
_CORBA = CorbaNameServiceClient(host_port=settings.CORBA_NS_HOST_PORT, context_name=settings.CORBA_NS_CONTEXT)
_WHOIS = SimpleLazyObject(lambda: _CORBA.get_object('Whois2', Whois.WhoisIntf))
_LOGGER = SimpleLazyObject(lambda: _CORBA.get_object('Logger', CCREG_MODULE.Logger))


class RdapCorbaRecoder(CorbaRecoder):
    """Corba recoder for RDAP."""

    def __init__(self, coding='utf-8'):
        super(RdapCorbaRecoder, self).__init__(coding)
        self.add_recode_function(CCREG_MODULE.DateType, self._decode_date, self._identity)
        self.add_recode_function(CCREG_MODULE.DateTimeType, self._decode_datetime, self._identity)
        self.add_recode_function(Date, self._decode_date, self._identity)
        self.add_recode_function(DateTime, self._decode_datetime, self._identity)

    def _decode_date(self, value):
        return date(value.year, value.month, value.day)

    def _decode_datetime(self, value):
        result = datetime(value.date.year, value.date.month, value.date.day, value.hour, value.minute, value.second)
        result = timezone.make_aware(result, timezone.utc)
        # If time zones are disabled, change the time to the default timezone and remove the time zone.
        if not settings.USE_TZ:
            result = timezone.make_naive(result, timezone.get_default_timezone())
        return result


WHOIS = CorbaClientProxy(CorbaClient(_WHOIS, RdapCorbaRecoder(), Whois.INTERNAL_SERVER_ERROR))
LOGGER = CorbaClientProxy(CorbaClient(_LOGGER, CorbaRecoder('utf-8'), CCREG_MODULE.Logger.INTERNAL_SERVER_ERROR))
