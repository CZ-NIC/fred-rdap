"""
Utils for translating Corba objects to python dictionary
"""
from datetime import date, datetime


def unwrap_datetime(idl_datetime):
    return datetime(idl_datetime.date.year, idl_datetime.date.month, idl_datetime.date.day, idl_datetime.hour,
                    idl_datetime.minute, idl_datetime.second)


def unwrap_date(idl_date):
    return date(idl_date.year, idl_date.month, idl_date.day)

def nonempty(input):
    return input is not None and input != ''
