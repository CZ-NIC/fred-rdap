from django.conf import settings
from django.utils.functional import SimpleLazyObject

from pylogger.corbalogger import Logger

from .corba import Corba, importIDL

importIDL(settings.CORBA_IDL_ROOT_PATH + '/' + settings.CORBA_IDL_LOGGER_FILENAME)
_LOGGER_CORBA = Corba(ior=settings.CORBA_NS_HOST_PORT, context_name=settings.CORBA_NS_CONTEXT, export_modules=['ccReg'])
_LOGGER_OBJ = SimpleLazyObject(lambda: _LOGGER_CORBA.get_object('Logger', 'ccReg.Logger'))
_LOGGER_MODULE = _LOGGER_CORBA.ccReg
py_logger_obj = Logger(_LOGGER_OBJ, _LOGGER_MODULE)


def get_logger():
    return py_logger_obj
