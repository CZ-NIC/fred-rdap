"""
Utils for translating Corba objects to python dictionary
"""

from datetime import datetime

def unwrap_datetime(idl_datetime):
    return datetime(idl_datetime.date.year, idl_datetime.date.month, idl_datetime.date.day, idl_datetime.hour, idl_datetime.minute, idl_datetime.second)    
