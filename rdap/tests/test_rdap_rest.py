"""Tests for `rdap.rdap_rest` package."""
from django.test import SimpleTestCase, override_settings
from fred_idl.Registry import Date, DateTime
from fred_idl.Registry.Whois import Contact, ContactIdentification, DisclosableContactIdentification, \
    DisclosablePlaceAddress, DisclosableString, Domain, KeySet, NameServer, NSSet, PlaceAddress
from mock import patch, sentinel

from rdap.rdap_rest.domain import delete_candidate_domain_to_dict, domain_to_dict
from rdap.rdap_rest.entity import contact_to_dict
from rdap.rdap_rest.keyset import keyset_to_dict
from rdap.rdap_rest.nameserver import nameserver_to_dict
from rdap.rdap_rest.nsset import nsset_to_dict
from rdap.utils.corba import WHOIS


def get_contact():
    nothing = DisclosableString(value='', disclose=False)
    place = PlaceAddress(street1='', street2='', street3='', city='', stateorprovince='', postalcode='',
                         country_code='')
    address = DisclosablePlaceAddress(value=place, disclose=False)
    ident = DisclosableContactIdentification(
        value=ContactIdentification(identification_type='PASS', identification_data=''),
        disclose=False,
    )
    created = DateTime(Date(day=4, month=1, year=1980), hour=11, minute=14, second=10)
    return Contact(
        handle='KRYTEN', organization=nothing, name=nothing, address=address, phone=nothing, fax=nothing, email=nothing,
        notify_email=nothing, vat_number=nothing, identification=ident, creating_registrar_handle='HOLLY',
        sponsoring_registrar_handle='LISTER', created=created, changed=None, last_transfer=None, statuses=[])


def get_domain(admin_contact_handles=None, nsset_handle=None, keyset_handle=None):
    registered = DateTime(Date(day=1, month=1, year=1980), hour=12, minute=24, second=42)
    expire = Date(day=31, month=12, year=2032)
    expire_time = DateTime(Date(day=31, month=12, year=2032), hour=22, minute=35, second=59)
    return Domain(
        handle='example.cz', registrant_handle='KRYTEN', admin_contact_handles=(admin_contact_handles or []),
        nsset_handle=nsset_handle, keyset_handle=keyset_handle, registrar_handle=sentinel.registrar_handle, statuses=[],
        registered=registered, changed=None, last_transfer=None, expire=expire, expire_time_estimate=expire_time,
        expire_time_actual=None, validated_to=None, validated_to_time_estimate=None, validated_to_time_actual=None)


def get_nsset(nservers=None, tech_contact_handles=None):
    created = DateTime(Date(day=2, month=1, year=1980), hour=8, minute=35, second=47)
    return NSSet(
        handle='new-saturn', nservers=(nservers or []), tech_contact_handles=(tech_contact_handles or []),
        registrar_handle='LISTER', created=created, changed=None, last_transfer=None, statuses=[])


def get_keyset(tech_contact_handles=None):
    created = DateTime(Date(day=3, month=1, year=1980), hour=10, minute=9, second=34)
    return KeySet(
        handle='gazpacho', dns_keys=[], tech_contact_handles=(tech_contact_handles or []), registrar_handle='RIMMER',
        created=created, changed=None, last_transfer=None, statuses=[])


@override_settings(RDAP_ROOT_URL='http://rdap.example.cz/')
class TestDomainToDict(SimpleTestCase):
    """Test `rdap.rdap_rest.domain.domain_to_dict` function."""

    def test_simple(self):
        result = domain_to_dict(get_domain())
        self.assertEqual(result['links'][0]['value'], 'http://rdap.example.cz/domain/example.cz')
        self.assertEqual(result['entities'][0]['links'][0]['value'], 'http://rdap.example.cz/entity/KRYTEN')

    def test_admin_contacts(self):
        result = domain_to_dict(get_domain(admin_contact_handles=['HOLLY']))
        admin = result['entities'][2]
        self.assertEqual(admin['roles'], ['administrative'])
        self.assertEqual(admin['links'][0]['value'], 'http://rdap.example.cz/entity/HOLLY')

    def test_nsset(self):
        with patch.object(WHOIS, 'client', spec=('get_nsset_by_handle', )) as whois_mock:
            whois_mock.get_nsset_by_handle.return_value = get_nsset()

            result = domain_to_dict(get_domain(nsset_handle='new-saturn'))

        self.assertEqual(result['fred_nsset']['links'][0]['value'], 'http://rdap.example.cz/fred_nsset/new-saturn')

    def test_nameservers(self):
        nservers = [NameServer(fqdn='nameserver.example.cz', ip_addresses=[])]
        with patch.object(WHOIS, 'client', spec=('get_nsset_by_handle', )) as whois_mock:
            whois_mock.get_nsset_by_handle.return_value = get_nsset(nservers=nservers)

            result = domain_to_dict(get_domain(nsset_handle='new-saturn'))

        self.assertEqual(result['nameservers'][0]['links'][0]['value'],
                         'http://rdap.example.cz/nameserver/nameserver.example.cz')

    def test_keyset(self):
        with patch.object(WHOIS, 'client', spec=('get_keyset_by_handle', )) as whois_mock:
            whois_mock.get_keyset_by_handle.return_value = get_keyset()

            result = domain_to_dict(get_domain(keyset_handle='gazpacho'))

        self.assertEqual(result['fred_keyset']['links'][0]['value'], 'http://rdap.example.cz/fred_keyset/gazpacho')


@override_settings(RDAP_ROOT_URL='http://rdap.example.cz/')
class TestDeleteCandidateDomainToDict(SimpleTestCase):
    """Test `rdap.rdap_rest.domain.delete_candidate_domain_to_dict` function."""

    def test_simple(self):
        result = delete_candidate_domain_to_dict(get_domain())
        self.assertEqual(result['links'][0]['value'], 'http://rdap.example.cz/domain/example.cz')


@override_settings(RDAP_ROOT_URL='http://rdap.example.cz/')
class TestContactToDict(SimpleTestCase):
    """Test `rdap.rdap_rest.domain.contact_to_dict` function."""

    def test_simple(self):
        result = contact_to_dict(get_contact())
        self.assertEqual(result['links'][0]['value'], 'http://rdap.example.cz/entity/KRYTEN')


@override_settings(RDAP_ROOT_URL='http://rdap.example.cz/')
class TestKeysetToDict(SimpleTestCase):
    """Test `rdap.rdap_rest.domain.keyset_to_dict` function."""

    def test_simple(self):
        result = keyset_to_dict(get_keyset())
        self.assertEqual(result['links'][0]['value'], 'http://rdap.example.cz/fred_keyset/gazpacho')

    def test_tech_contacts(self):
        result = keyset_to_dict(get_keyset(tech_contact_handles=['KOCHANSKI']))
        tech = result['entities'][1]
        self.assertEqual(tech['roles'], ['technical'])
        self.assertEqual(tech['links'][0]['value'], 'http://rdap.example.cz/entity/KOCHANSKI')


@override_settings(RDAP_ROOT_URL='http://rdap.example.cz/')
class TestNameserverToDict(SimpleTestCase):
    """Test `rdap.rdap_rest.domain.nameserver_to_dict` function."""

    def test_simple(self):
        nameserver = NameServer(fqdn='nameserver.example.cz', ip_addresses=[])
        result = nameserver_to_dict(nameserver)
        self.assertEqual(result['links'][0]['value'], 'http://rdap.example.cz/nameserver/nameserver.example.cz')


@override_settings(RDAP_ROOT_URL='http://rdap.example.cz/')
class TestNssetToDict(SimpleTestCase):
    """Test `rdap.rdap_rest.domain.nsset_to_dict` function."""

    def test_simple(self):
        result = nsset_to_dict(get_nsset())
        self.assertEqual(result['links'][0]['value'], 'http://rdap.example.cz/fred_nsset/new-saturn')

    def test_tech_contacts(self):
        result = nsset_to_dict(get_nsset(tech_contact_handles=['KOCHANSKI']))
        tech = result['entities'][1]
        self.assertEqual(tech['roles'], ['technical'])
        self.assertEqual(tech['links'][0]['value'], 'http://rdap.example.cz/entity/KOCHANSKI')

    def test_nameservers(self):
        nservers = [NameServer(fqdn='nameserver.example.cz', ip_addresses=[])]
        result = nsset_to_dict(get_nsset(nservers=nservers))
        self.assertEqual(result['nameservers'][0]['links'][0]['value'],
                         'http://rdap.example.cz/nameserver/nameserver.example.cz')
