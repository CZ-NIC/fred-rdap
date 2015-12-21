"""
Utils for translating Corba objects to python dictionary
"""
from datetime import date, datetime
from django.conf import settings
import logging


def unwrap_datetime(idl_datetime):
    return datetime(idl_datetime.date.year, idl_datetime.date.month, idl_datetime.date.day, idl_datetime.hour,
                    idl_datetime.minute, idl_datetime.second)


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


EPP_TO_RDAP_STATUS_MAPPING = {
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
}


CUSTOM_TO_RDAP_STATUS_MAPPING = {
    'validatedContact': 'validated',
    'contactPassedManualVerification': 'validated',
    'deleteCandidate': 'pending delete',
    'outzone': 'inactive',
}


STATUS_MAPPING = (
    EPP_TO_RDAP_STATUS_MAPPING,
    CUSTOM_TO_RDAP_STATUS_MAPPING,
)


def rdap_status_mapping(status_list):
    if not status_list:
        status_list = ['ok']
    ret = set()
    for status in status_list:
        for mapping in STATUS_MAPPING:
            mapped_value = mapping.get(status)
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
