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
"""Wrapper module to whois idl interface."""
import logging
from typing import Any, Dict, Optional

from django.http import HttpRequest
from regal.exceptions import ObjectDoesNotExist

from rdap.utils.corba import CONTACT_CLIENT, DOMAIN_CLIENT, KEYSET_CLIENT, NSSET_CLIENT

from .domain import domain_to_dict
from .entity import contact_to_dict
from .keyset import keyset_to_dict
from .nameserver import nameserver_to_dict
from .nsset import nsset_to_dict


def get_contact_by_handle(request: HttpRequest, handle: str) -> Optional[Dict[str, Any]]:
    """Get contact by handle and return RDAP structure."""
    logging.debug('get_contact_by_handle: %s', handle)
    contact = CONTACT_CLIENT.get_contact_info(CONTACT_CLIENT.get_contact_id(handle))
    return contact_to_dict(contact, request)


def get_domain_by_handle(request: HttpRequest, handle: str) -> Optional[Dict[str, Any]]:
    logging.debug('get_domain_by_handle: %s', handle)
    domain = DOMAIN_CLIENT.get_domain_info(DOMAIN_CLIENT.get_domain_id(handle))
    return domain_to_dict(domain, request)


def get_nameserver_by_handle(request: HttpRequest, handle: str) -> Dict[str, Any]:
    logging.debug('get_nameserver_by_handle: %s', handle)
    if NSSET_CLIENT.check_dns_host(handle):
        return nameserver_to_dict(handle, request)
    else:
        raise ObjectDoesNotExist()


def get_nsset_by_handle(request: HttpRequest, handle: str) -> Optional[Dict[str, Any]]:
    logging.debug('get_nsset_by_handle: %s', handle)
    nsset = NSSET_CLIENT.get_nsset_info(NSSET_CLIENT.get_nsset_id(handle))
    return nsset_to_dict(nsset, request)


def get_keyset_by_handle(request: HttpRequest, handle: str) -> Optional[Dict[str, Any]]:
    logging.debug('get_keyset_by_handle: %s', handle)
    keyset = KEYSET_CLIENT.get_keyset_info(KEYSET_CLIENT.get_keyset_id(handle))
    return keyset_to_dict(keyset, request)
