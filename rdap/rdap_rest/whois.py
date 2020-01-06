#
# Copyright (C) 2014-2020  CZ.NIC, z. s. p. o.
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

"""Wrapper module to whois idl interface."""
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


def get_contact_by_handle(request, handle):
    logging.debug('get_contact_by_handle: %s', handle)
    try:
        return contact_to_dict(request, WHOIS.get_contact_by_handle(handle))
    except OBJECT_NOT_FOUND:
        raise NotFoundError()
    except INVALID_HANDLE:
        raise InvalidHandleError()


def get_domain_by_handle(request, handle):
    logging.debug('get_domain_by_handle: %s', handle)
    try:
        return domain_to_dict(request, WHOIS.get_domain_by_handle(handle))
    except OBJECT_DELETE_CANDIDATE:
        return delete_candidate_domain_to_dict(request, handle)
    except (OBJECT_NOT_FOUND, TOO_MANY_LABELS, UNMANAGED_ZONE):
        raise NotFoundError()
    except INVALID_LABEL:
        raise InvalidHandleError()


def get_nameserver_by_handle(request, handle):
    logging.debug('get_nameserver_by_handle: %s', handle)
    try:
        return nameserver_to_dict(request, WHOIS.get_nameserver_by_fqdn(handle))
    except OBJECT_NOT_FOUND:
        raise NotFoundError()
    except INVALID_HANDLE:
        raise InvalidHandleError()


def get_nsset_by_handle(request, handle):
    logging.debug('get_nsset_by_handle: %s', handle)
    try:
        return nsset_to_dict(request, WHOIS.get_nsset_by_handle(handle))
    except OBJECT_NOT_FOUND:
        raise NotFoundError()
    except INVALID_HANDLE:
        raise InvalidHandleError()


def get_keyset_by_handle(request, handle):
    logging.debug('get_keyset_by_handle: %s', handle)
    try:
        return keyset_to_dict(request, WHOIS.get_keyset_by_handle(handle))
    except OBJECT_NOT_FOUND:
        raise NotFoundError()
    except INVALID_HANDLE:
        raise InvalidHandleError()
