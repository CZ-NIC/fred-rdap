#!/usr/bin/python
#
# Copyright (C) 2014-2022  CZ.NIC, z. s. p. o.
#
# This file is part of FRED.
#
# FRED is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FRED is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FRED.  If not, see <https://www.gnu.org/licenses/>.
#
from datetime import datetime
from typing import cast

from django.conf import settings
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from fred_idl.Registry import IsoDate, IsoDateTime, Whois
from frgal import make_credentials
from frgal.aio import SyncGrpcProxy
from pyfco import CorbaClient, CorbaClientProxy, CorbaNameServiceClient, CorbaRecoder
from pyfco.recoder import decode_iso_date, decode_iso_datetime
from regal import ContactClient, DomainClient, KeysetClient, NssetClient

from rdap.settings import RDAP_SETTINGS

_CORBA = CorbaNameServiceClient(host_port=RDAP_SETTINGS.CORBA_NETLOC,
                                context_name=RDAP_SETTINGS.CORBA_CONTEXT)
_WHOIS = SimpleLazyObject(lambda: _CORBA.get_object('Whois2', Whois.WhoisIntf))


class RdapCorbaRecoder(CorbaRecoder):
    """Corba recoder for RDAP."""

    def __init__(self, coding: str = 'utf-8') -> None:
        super(RdapCorbaRecoder, self).__init__(coding)
        self.add_recode_function(IsoDate, decode_iso_date, self._identity)
        self.add_recode_function(IsoDateTime, self._decode_iso_datetime, self._identity)

    def _decode_iso_datetime(self, value: IsoDateTime) -> datetime:
        """Decode `IsoDateTime` struct to datetime object with respect to the timezone settings."""
        result = cast(datetime, decode_iso_datetime(value))
        if not settings.USE_TZ:
            result = timezone.make_naive(result, timezone.get_default_timezone())
        return result


WHOIS = CorbaClientProxy(CorbaClient(_WHOIS, RdapCorbaRecoder(), Whois.INTERNAL_SERVER_ERROR))
CONTACT_CLIENT = SyncGrpcProxy(ContactClient(RDAP_SETTINGS.REGISTRY_NETLOC,
                                             make_credentials(RDAP_SETTINGS.REGISTRY_SSL_CERT)))
DOMAIN_CLIENT = SyncGrpcProxy(DomainClient(RDAP_SETTINGS.REGISTRY_NETLOC,
                                           make_credentials(RDAP_SETTINGS.REGISTRY_SSL_CERT)))
KEYSET_CLIENT = SyncGrpcProxy(KeysetClient(RDAP_SETTINGS.REGISTRY_NETLOC,
                                           make_credentials(RDAP_SETTINGS.REGISTRY_SSL_CERT)))
NSSET_CLIENT = SyncGrpcProxy(NssetClient(RDAP_SETTINGS.REGISTRY_NETLOC,
                                         make_credentials(RDAP_SETTINGS.REGISTRY_SSL_CERT)))
