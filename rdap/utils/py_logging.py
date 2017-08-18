from django.utils.functional import SimpleLazyObject
from pylogger.corbalogger import Logger

from .corba import CCREG_MODULE, LOGGER

py_logger_obj = SimpleLazyObject(lambda: Logger(LOGGER, CCREG_MODULE))
