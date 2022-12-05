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
from frgal import make_credentials
from frgal.aio import SyncGrpcProxy
from regal import ContactClient, DomainClient, KeysetClient, NssetClient

from rdap.settings import RDAP_SETTINGS

CONTACT_CLIENT = SyncGrpcProxy(ContactClient(RDAP_SETTINGS.REGISTRY_NETLOC,
                                             make_credentials(RDAP_SETTINGS.REGISTRY_SSL_CERT)))
DOMAIN_CLIENT = SyncGrpcProxy(DomainClient(RDAP_SETTINGS.REGISTRY_NETLOC,
                                           make_credentials(RDAP_SETTINGS.REGISTRY_SSL_CERT)))
KEYSET_CLIENT = SyncGrpcProxy(KeysetClient(RDAP_SETTINGS.REGISTRY_NETLOC,
                                           make_credentials(RDAP_SETTINGS.REGISTRY_SSL_CERT)))
NSSET_CLIENT = SyncGrpcProxy(NssetClient(RDAP_SETTINGS.REGISTRY_NETLOC,
                                         make_credentials(RDAP_SETTINGS.REGISTRY_SSL_CERT)))
