#
# Copyright (C) 2021-2022  CZ.NIC, z. s. p. o.
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
"""RDAP constants."""
from enum import Enum, unique

LOGGER_SERVICE = 'RDAP'


@unique
class LogResult(str, Enum):
    """Result values for log."""

    SUCCESS = 'Ok'
    NOT_FOUND = 'NotFound'
    BAD_REQUEST = 'BadRequest'
    INTERNAL_SERVER_ERROR = 'InternalServerError'


@unique
class LogEntryType(str, Enum):
    """Result values for log."""

    ENTITY_LOOKUP = 'EntityLookup'
    DOMAIN_LOOKUP = 'DomainLookup'
    NAMESERVER_LOOKUP = 'NameserverLookup'
    NSSET_LOOKUP = 'NSSetLookup'
    KEYSET_LOOKUP = 'KeySetLookup'


@unique
class ObjectStatus(str, Enum):
    """Important object statuses."""

    LINKED = 'linked'
    DELETE_CANDIDATE = 'deleteCandidate'


@unique
class Publish(str, Enum):
    """Publish field names."""

    NAME = 'name'
    ORGANIZATION = 'organization'
    EMAILS = 'emails'
    TELEPHONE = 'telephone'
    FAX = 'fax'
    PLACE = 'place'
