#!/usr/bin/env python
"""Mock Fred server for conformance tests."""
import sys

import CosNaming
from fred_idl import Registry__POA, ccReg__POA
from fred_idl.ccReg import RequestServiceListItem, RequestTypeListItem, ResultCodeListItem
from fred_idl.Registry import IsoDate, IsoDateTime
from fred_idl.Registry.Whois import Contact, ContactIdentification, DisclosableContactIdentification, \
    DisclosablePlaceAddress, DisclosableString, Domain, KeySet, NameServer, NSSet, PlaceAddress, OBJECT_NOT_FOUND
from omniORB import CORBA


class FakeLogger(ccReg__POA.Logger):
    """Implementation of logger interface."""

    def getServices(self, *args):
        print("{}.getServices{}".format(self.__class__.__name__, args))
        return [RequestServiceListItem(9, 'RDAP')]

    def getRequestTypesByService(self, *args):
        print("{}.getRequestTypesByService{}".format(self.__class__.__name__, args))
        return [RequestTypeListItem(2001, 'EntityLookup'),
                RequestTypeListItem(3002, 'DomainLookup'),
                RequestTypeListItem(3003, 'NameserverLookup'),
                RequestTypeListItem(3101, 'NSSetLookup'),
                RequestTypeListItem(3102, 'KeySetLookup')]

    def getResultCodesByService(self, *args):
        print("{}.getResultCodesByService{}".format(self.__class__.__name__, args))
        return [ResultCodeListItem(61, 'Ok'),
                ResultCodeListItem(62, 'NotFound'),
                ResultCodeListItem(63, 'InternalServerError'),
                ResultCodeListItem(64, 'BadRequest')]

    def createRequest(self, *args):
        print("{}.createRequest{}".format(self.__class__.__name__, args))
        return 42

    def closeRequest(self, *args):
        print("{}.closeRequest{}".format(self.__class__.__name__, args))
        return None


class FakeWhois(Registry__POA.Whois.WhoisIntf):
    """Implementation of whois interface."""

    def get_contact_by_handle(self, handle):
        print("{}.get_contact_by_handle({})".format(self.__class__.__name__, handle))
        if handle == 'KOCHANSKI':
            raise OBJECT_NOT_FOUND()
        nothing = DisclosableString('', False)
        no_address = DisclosablePlaceAddress(PlaceAddress('', '', '', '', '', '', ''), False)
        no_ident = DisclosableContactIdentification(ContactIdentification('OP', ''), False)
        return Contact(handle, nothing, nothing, no_address, nothing, nothing, nothing, nothing, nothing, no_ident,
                       'REGGIE', 'REGGIE', IsoDateTime('1970-01-01T00:00:00Z'), None, None, [])

    def get_nsset_by_handle(self, handle):
        print("{}.get_nsset_by_handle({})".format(self.__class__.__name__, handle))
        return NSSet(handle, [], [], 'REGGIE', IsoDateTime('1970-01-01T00:00:00Z'), None, None, [])

    def get_nameserver_by_fqdn(self, fqdn):
        print("{}.get_nameserver_by_fqdn({})".format(self.__class__.__name__, fqdn))
        if fqdn == 'ace.rimmer.cz':
            raise OBJECT_NOT_FOUND()
        return NameServer(fqdn, [])

    def get_keyset_by_handle(self, handle):
        print("{}.get_keyset_by_handle({})".format(self.__class__.__name__, handle))
        return KeySet(handle, [], [], 'REGGIE', IsoDateTime('1970-01-01T00:00:00Z'), None, None, [])

    def get_domain_by_handle(self, handle):
        print("{}.get_domain_by_handle({})".format(self.__class__.__name__, handle))
        if handle == 'kochanski.cz':
            raise OBJECT_NOT_FOUND()
        return Domain(handle, 'LISTER', [], None, None, 'REGGIE', [], IsoDateTime('1970-01-01T00:00:00Z'), None, None,
                      IsoDate('2030-01-01'), IsoDateTime('2030-01-01T00:00:00Z'), None, None, None, None)


def bind_interface(context, interface, name):
    """Bind the Corba object to the context by its name."""
    interface_instance = interface()
    corba_object = interface_instance._this()
    cos_name = [CosNaming.NameComponent(name, "Object")]
    try:
        context.bind(cos_name, corba_object)
        print("New {} object bound".format(name))

    except CosNaming.NamingContext.AlreadyBound:
        context.rebind(cos_name, corba_object)
        print("{} binding already existed -- rebound".format(name))


def run_services():
    """Run the services."""
    # Initialise the ORB and find the root POA
    orb = CORBA.ORB_init(sys.argv or ['-ORBnativeCharCodeSet', 'UTF-8'], CORBA.ORB_ID)
    poa = orb.resolve_initial_references("RootPOA")

    # Obtain a reference to the root naming context
    obj = orb.resolve_initial_references("NameService")
    rootContext = obj._narrow(CosNaming.NamingContext)

    if rootContext is None:
        print "Failed to narrow the root naming context"
        sys.exit(1)

    # Bind a context named "test.my_context" to the root context
    name = [CosNaming.NameComponent("fred", "context")]
    try:
        testContext = rootContext.bind_new_context(name)
        print "New test context bound"
    except CosNaming.NamingContext.AlreadyBound:
        print "Test context already exists"
        obj = rootContext.resolve(name)
        testContext = obj._narrow(CosNaming.NamingContext)
        if testContext is None:
            print "fred.context exists but is not a NamingContext"
            sys.exit(1)

    bind_interface(testContext, FakeWhois, "Whois2")
    bind_interface(testContext, FakeLogger, "Logger")

    # Activate the POA
    poaManager = poa._get_the_POAManager()
    poaManager.activate()

    # Block for ever (or until the ORB is shut down)
    orb.run()


def main():
    """Main program."""
    try:
        run_services()
    except Exception:
        exit(1)


if __name__ == '__main__':
    main()
