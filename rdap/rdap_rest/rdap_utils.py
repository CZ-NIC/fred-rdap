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

"""Utils for translating Corba objects to python dictionary."""
import idna
from django.conf import settings
from django.utils import timezone


def to_rfc3339(dt):
    """Format datetime object as in rfc3339 (with stripped microsecond part)."""
    if timezone.is_aware(dt) and not settings.USE_TZ:
        raise TypeError("can't compare offset-naive and offset-aware datetimes")

    aux = dt.replace(microsecond=0)

    if timezone.is_aware(dt):
        aux = aux.replace(tzinfo=dt.tzinfo)
    else:
        aux = timezone.make_aware(aux, timezone.get_default_timezone())

    return aux.isoformat('T')


def nonempty(input):
    return input is not None and input != ''


def disclosable_nonempty(disclosable):
    """Check if value which can be hidden by user setting should be added to output."""
    if disclosable.disclose:
        return nonempty(disclosable.value)
    else:
        return False


RDAP_STATUS_MAPPING = {
    # EPP defined
    # https://tools.ietf.org/html/rfc7483#section-10.2.2
    # https://tools.ietf.org/html/rfc8056
    'addPeriod': 'add period',
    'autoRenewPeriod': 'auto renew period',
    'clientDeleteProhibited': 'client delete prohibited',
    'clientHold': 'client hold',
    'clientRenewProhibited': 'client renew prohibited',
    'clientTransferProhibited': 'client transfer prohibited',
    'clientUpdateProhibited': 'client update prohibited',
    'inactive': 'inactive',
    'linked': 'associated',
    'ok': 'active',
    'pendingCreate': 'pending create',
    'pendingDelete': 'pending delete',
    'pendingRenew': 'pending renew',
    'pendingRestore': 'pending restore',
    'pendingTransfer': 'pending transfer',
    'pendingUpdate': 'pending update',
    'redemptionPeriod': 'redemption period',
    'renewPeriod': 'renew period',
    'serverDeleteProhibited': 'server delete prohibited',
    'serverRenewProhibited': 'server renew prohibited',
    'serverTransferProhibited': 'server transfer prohibited',
    'serverUpdateProhibited': 'server update prohibited',
    'serverHold': 'server hold',
    'transferPeriod': 'transfer period',
    # FRED custom
    'validatedContact': 'validated',
    'contactPassedManualVerification': 'validated',
    'deleteCandidate': 'pending delete',
    'outzone': 'inactive',
}


def rdap_status_mapping(status_list):
    """
    Translate backend status identifiers to rdap values.

    ('ok' status is not returned by backend and it is represented
    with empty input list - means no restrictions or pending operations)

    @rtype: list
    """
    if not status_list:
        status_list = ['ok']
    ret = set()
    for status in status_list:
        mapped_value = RDAP_STATUS_MAPPING.get(status)
        if mapped_value:
            ret.add(mapped_value)
    return list(ret)


class ObjectClassName(object):
    DOMAIN = 'domain'
    ENTITY = 'entity'
    NAMESERVER = 'nameserver'
    NSSET = 'fred_nsset'
    KEYSET = 'fred_keyset'


class InvalidIdn(Exception):
    """Invalid input - internationalized domain name."""


def preprocess_fqdn(fqdn):
    """Normalize fqdn input search string for backend call.

    @rtype: str
    """
    try:
        fqdn = idna.encode(fqdn)
        idna.decode(fqdn)
    except UnicodeError:
        raise InvalidIdn()
    return fqdn.decode()


def add_unicode_name(dst_dict, ldh_name):
    """Add optional unicodeName key to dictionary if contains non-ascii characters."""
    unicode_name = ldh_name.encode("idna").decode("idna")
    if unicode_name != ldh_name:
        dst_dict["unicodeName"] = unicode_name
