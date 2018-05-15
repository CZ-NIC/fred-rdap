"""Utils for translating Corba objects to python dictionary."""
from __future__ import unicode_literals

import idna
import six
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

    if six.PY2:
        format_string = b'T'
    else:
        format_string = 'T'
    return aux.isoformat(format_string)


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
    #
    # empty values will be added from draft
    # https://tools.ietf.org/html/draft-gould-epp-rdap-status-mapping-02
    'addPeriod': '',
    'autoRenewPeriod': '',
    'clientDeleteProhibited': '',
    'clientHold': '',
    'clientRenewProhibited': '',
    'clientTransferProhibited': '',
    'clientUpdateProhibited': '',
    'inactive': 'inactive',
    'linked': 'associated',
    'ok': 'active',
    'pendingCreate': 'pending create',
    'pendingDelete': 'pending delete',
    'pendingRenew': 'pending renew',
    'pendingRestore': '',
    'pendingTransfer': 'pending transfer',
    'pendingUpdate': 'pending update',
    'redemptionPeriod': '',
    'renewPeriod': '',
    'serverDeleteProhibited': '',
    'serverRenewProhibited': '',
    'serverTransferProhibited': '',
    'serverUpdateProhibited': '',
    'serverHold': '',
    'transferPeriod': '',
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


def get_disclaimer_text():
    if get_disclaimer_text.text is None:
        with open(settings.DISCLAIMER_FILE, 'r') as file:
            get_disclaimer_text.text = file.read()

    return get_disclaimer_text.text


get_disclaimer_text.text = None


class ObjectClassName(object):
    DOMAIN = 'domain'
    ENTITY = 'entity'
    NAMESERVER = 'nameserver'
    NSSET = 'fred_nsset'
    KEYSET = 'fred_keyset'


class InvalidIdn(Exception):
    """Invalid input - internationalized domain name."""


def preprocess_fqdn(fqdn):
    """Normalize fqdn input search string for backend call."""
    try:
        fqdn = idna.encode(fqdn)
        idna.decode(fqdn)
    except UnicodeError:
        raise InvalidIdn()
    return fqdn


def add_unicode_name(dst_dict, ldh_name):
    """Add optional unicodeName key to dictionary if contains non-ascii characters."""
    if six.PY3:
        unicode_name = ldh_name.encode("idna").decode("idna")
    else:
        unicode_name = ldh_name.decode("idna")
    if unicode_name != ldh_name:
        dst_dict["unicodeName"] = unicode_name
