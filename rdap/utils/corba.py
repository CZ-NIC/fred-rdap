#!/usr/bin/python
# -*- coding: utf-8 -*-
import os.path

import omniORB
from django.conf import settings
from django.utils.functional import SimpleLazyObject
from pyfco import CorbaNameServiceClient


def _get_registry_module():
    """Return `Registry` module."""
    try:
        import Registry
    except ImportError:
        Registry = None

    if not hasattr(Registry, 'Whois'):
        omniORB.importIDL(os.path.join(settings.CORBA_IDL_ROOT_PATH, settings.CORBA_IDL_WHOIS_FILENAME))
        import Registry
    return Registry


def _get_ccreg_module():
    """Return `ccReg` module."""
    try:
        import ccReg
    except ImportError:
        ccReg = None

    if not hasattr(ccReg, 'Logger'):
        omniORB.importIDL(os.path.join(settings.CORBA_IDL_ROOT_PATH, settings.CORBA_IDL_LOGGER_FILENAME))
        import ccReg
    return ccReg


REGISTRY_MODULE = SimpleLazyObject(_get_registry_module)
CCREG_MODULE = SimpleLazyObject(_get_ccreg_module)
_CORBA = CorbaNameServiceClient(host_port=settings.CORBA_NS_HOST_PORT, context_name=settings.CORBA_NS_CONTEXT)
WHOIS = SimpleLazyObject(lambda: _CORBA.get_object('Whois2', REGISTRY_MODULE.Whois.WhoisIntf))
LOGGER = SimpleLazyObject(lambda: _CORBA.get_object('Logger', CCREG_MODULE.Logger))
