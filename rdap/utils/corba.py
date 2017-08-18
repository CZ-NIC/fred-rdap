#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import sys
import types
import os.path

import CosNaming
import omniORB
from django.conf import settings
from django.utils.functional import SimpleLazyObject
from omniORB import CORBA, importIDL
from pyfco import CorbaNameServiceClient


# own exceptions
class IorNotFoundError(Exception):
    pass


class AlreadyLoggedInError(Exception):
    pass


class NotLoggedInError(Exception):
    pass


class LanguageNotSupportedError(Exception):
    pass


class SetLangAfterLoginError(Exception):
    pass


class ParameterIsNotListOrTupleError(Exception):
    pass


def transientFailure(cookie, retries, exc):
    if retries > 10:
        return False
    else:
        return True


def commFailure(cookie, retries, exc):
    if retries > 20:
        return False
    else:
        return True


def systemFailure(cookie, retries, exc):
    if retries > 5:
        return False
    else:
        return True


cookie = None
omniORB.installTransientExceptionHandler(cookie, transientFailure)
omniORB.installCommFailureExceptionHandler(cookie, commFailure)
omniORB.installSystemExceptionHandler(cookie, systemFailure)


# http://omniorb.sourceforge.net/omnipy3/omniORBpy/omniORBpy004.html
# ["-ORBnativeCharCodeSet", "UTF-8",
# "-ORBtraceLevel", "40"
# "-ORBtraceExceptions", "1",
# "-ORBtraceFile", "/tmp/debug-corba.log"]
orb = CORBA.ORB_init(["-ORBnativeCharCodeSet", "UTF-8"], CORBA.ORB_ID)

corbas = {}  # list of corba objects, one per each module that needs it (key to dict is name of module)
# list of path of already imported idl modules, so we dont import same modules multiple times (it's time consuming)
imported_idls = []


class Corba(object):
    def __init__(self, ior='localhost', context_name='fred', export_modules=None):
        object.__init__(self)
        self.ior = ior
        self.context_name = context_name
        self.context = None
        self.orb = orb

        # assign modules as attribute of this instance (i.e. corba.ccReg = sys.modules['ccReg'])
        if export_modules:
            for mod in export_modules:
                setattr(self, mod, sys.modules[mod])

    def connect(self):
        obj = orb.string_to_object('corbaname::' + self.ior)
        self.context = obj._narrow(CosNaming.NamingContext)

    def get_object(self, name, idl_type_str):
        if self.context is None:
            self.connect()
        cosname = [CosNaming.NameComponent(self.context_name, "context"),
                   CosNaming.NameComponent(name, "Object")]
        obj = self.context.resolve(cosname)

        # get idl type from idl_type_str:
        idl_type_parts = idl_type_str.split('.')
        idl_type = getattr(self, idl_type_parts[0])  # e.g. self.ccReg
        for part in idl_type_parts[1:]:
            idl_type = getattr(idl_type, part)

        return obj._narrow(idl_type)


def create_corba_for_module(mod_name):
    mod_settings = getattr(settings, mod_name.upper(), None)
    if mod_settings is None:
        return

    idls = getattr(mod_settings, 'CORBA_IDL', None)
    if idls is None:
        return
    logging.debug('Creating corba for module %s', mod_name)
    # Compile and import modules from idl. That modules can be found in sys.module[module_name]:
    if isinstance(idls, types.StringTypes):
        idls = [idls]
    for idl in idls:
        if idl not in imported_idls:  # check to avoid multiple import of the same idl
            importIDL(idl)
            imported_idls.append(idl)

    corbas[mod_name] = Corba(ior=mod_settings.CORBA_IOR,
                             context_name=mod_settings.CORBA_CONTEXT,
                             export_modules=getattr(mod_settings, 'CORBA_EXPORT_MODULES', None))


def create_corba_in_dynamic_modules():
    for app in settings.INSTALLED_APPS:
        create_corba_for_module(app)


def get_corba_for_module(mod_name):
    corba = corbas.get(mod_name)
    if corba is not None:
        return corba
    else:
        create_corba_for_module(mod_name)
        return corbas.get(mod_name)


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
