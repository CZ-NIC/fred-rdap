"""
Utils for translating Corba objects to python dictionary
"""
from datetime import date, datetime
from django.conf import settings


def unwrap_datetime(idl_datetime):
    return datetime(idl_datetime.date.year, idl_datetime.date.month, idl_datetime.date.day, idl_datetime.hour,
                    idl_datetime.minute, idl_datetime.second)


def unwrap_date(idl_date):
    return date(idl_date.year, idl_date.month, idl_date.day)


def nonempty(input):
    return input is not None and input != ''


def disclosable_nonempty(disclosable):
    if disclosable.disclose:
        return nonempty(disclosable.value)
    else:
        return False


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
