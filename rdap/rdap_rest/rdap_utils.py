"""
Utils for translating Corba objects to python dictionary
"""
from datetime import date, datetime

from django.conf import settings
from django.utils import timezone


def unwrap_datetime(idl_datetime):
    """
    Converts IDL datetime struct to python datetime.datetime.
    """
    dt = datetime(
        idl_datetime.date.year, idl_datetime.date.month, idl_datetime.date.day,
        idl_datetime.hour, idl_datetime.minute, idl_datetime.second
    )
    dt = timezone.make_aware(dt, timezone.utc)
    if not settings.USE_TZ:
        dt = timezone.make_naive(dt, timezone.get_default_timezone())
    return dt


def to_rfc3339(dt):
    """
    Simple function to format datetime object as in rfc3339 (with stripped microsecond part).
    """
    if timezone.is_aware(dt) and not settings.USE_TZ:
        raise TypeError("can't compare offset-naive and offset-aware datetimes")

    aux = dt.replace(microsecond=0)

    if timezone.is_aware(dt):
        aux = aux.replace(tzinfo=dt.tzinfo)
    else:
        aux = timezone.make_aware(aux, timezone.get_default_timezone())

    return aux.isoformat('T')


def unwrap_date(idl_date):
    return date(idl_date.year, idl_date.month, idl_date.day)


def nonempty(input):
    return input is not None and input != ''


def disclosable_nonempty(disclosable):
    """
    Check if value which can be hidden by user setting should be added to output
    """
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
    Translates backend status identifiers to rdap values

    ('ok' status is not returned by backend and it is represented
    with empty input list - means no restrictions or pending operations)
    """
    if not status_list:
        status_list = ['ok']
    ret = set()
    for status in status_list:
        mapped_value = RDAP_STATUS_MAPPING.get(status)
        if mapped_value:
            ret.add(mapped_value)
    return ret


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
    NSSET = 'nsset'
    KEYSET = 'keyset'


class InvalidIdn(Exception):
    """
    Invalid input - internationalized domain name
    """

def preprocess_fqdn(fqdn):
    """
    Normalize fqdn input search string for backend call
    """
    try:
        # Should be replaced by python-idna lib call
        # fqdn = idna.encode(fqdn)
        #
        # Current python (2.7) idna encoding implements rfc3490
        # but it is obsoleted by rfc5890, rfc5891
        fqdn = fqdn.encode('idna')
        fqdn.decode('idna')
    except UnicodeError, e:
        raise InvalidIdn()
    return fqdn
