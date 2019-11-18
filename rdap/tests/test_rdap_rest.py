#
# Copyright (C) 2017-2019  CZ.NIC, z. s. p. o.
#
# This file is part of FRED.
#
# FRED is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FRED is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FRED.  If not, see <https://www.gnu.org/licenses/>.

"""Tests for `rdap.rdap_rest` package."""
from __future__ import unicode_literals

from datetime import date, datetime

from django.test import RequestFactory, SimpleTestCase, override_settings
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
    return Contact(
        handle='KRYTEN', organization=nothing, name=nothing, address=address, phone=nothing, fax=nothing, email=nothing,
        notify_email=nothing, vat_number=nothing, identification=ident, creating_registrar_handle='HOLLY',
        sponsoring_registrar_handle='LISTER', created=datetime(1980, 1, 4, 11, 14, 10), changed=None,
        last_transfer=None, statuses=[])


def get_domain(admin_contact_handles=None, nsset_handle=None, keyset_handle=None):
    return Domain(
        handle='example.cz', registrant_handle='KRYTEN', admin_contact_handles=(admin_contact_handles or []),
        nsset_handle=nsset_handle, keyset_handle=keyset_handle, registrar_handle=sentinel.registrar_handle, statuses=[],
        registered=datetime(1980, 1, 1, 12, 24, 42), changed=None, last_transfer=None, expire=date(2032, 12, 31),
        expire_time_estimate=datetime(2032, 12, 31, 22, 35, 59), expire_time_actual=None, validated_to=None,
        validated_to_time_estimate=None, validated_to_time_actual=None)


def get_nsset(nservers=None, tech_contact_handles=None):
    return NSSet(
        handle='new-saturn', nservers=(nservers or []), tech_contact_handles=(tech_contact_handles or []),
        registrar_handle='LISTER', created=datetime(1980, 1, 2, 8, 35, 47), changed=None, last_transfer=None,
        statuses=[])


def get_keyset(tech_contact_handles=None):
    return KeySet(
        handle='gazpacho', dns_keys=[], tech_contact_handles=(tech_contact_handles or []), registrar_handle='RIMMER',
        created=datetime(1980, 1, 3, 10, 9, 34), changed=None, last_transfer=None, statuses=[])


@override_settings(ALLOWED_HOSTS=['rdap.example'], RDAP_UNIX_WHOIS=None)
class TestDomainToDict(SimpleTestCase):
    """Test `rdap.rdap_rest.domain.domain_to_dict` function."""

    def setUp(self):
        self.request = RequestFactory(HTTP_HOST='rdap.example').get('/dummy/')

    def test_simple(self):
        result = domain_to_dict(self.request, get_domain())
        self.assertEqual(result['links'][0]['value'], 'http://rdap.example/domain/example.cz')
        self.assertEqual(result['entities'][0]['links'][0]['value'], 'http://rdap.example/entity/KRYTEN')
        self.assertNotIn('port43', result)

    def test_admin_contacts(self):
        result = domain_to_dict(self.request, get_domain(admin_contact_handles=['HOLLY']))
        admin = result['entities'][2]
        self.assertEqual(admin['roles'], ['administrative'])
        self.assertEqual(admin['links'][0]['value'], 'http://rdap.example/entity/HOLLY')

    def test_nsset(self):
        with patch.object(WHOIS, 'client', spec=('get_nsset_by_handle', )) as whois_mock:
            whois_mock.get_nsset_by_handle.return_value = get_nsset()

            result = domain_to_dict(self.request, get_domain(nsset_handle='new-saturn'))

        self.assertEqual(result['fred_nsset']['links'][0]['value'], 'http://rdap.example/fred_nsset/new-saturn')

    def test_nameservers(self):
        nservers = [NameServer(fqdn='nameserver.example.cz', ip_addresses=[])]
        with patch.object(WHOIS, 'client', spec=('get_nsset_by_handle', )) as whois_mock:
            whois_mock.get_nsset_by_handle.return_value = get_nsset(nservers=nservers)

            result = domain_to_dict(self.request, get_domain(nsset_handle='new-saturn'))

        self.assertEqual(result['nameservers'][0]['links'][0]['value'],
                         'http://rdap.example/nameserver/nameserver.example.cz')

    def test_keyset(self):
        with patch.object(WHOIS, 'client', spec=('get_keyset_by_handle', )) as whois_mock:
            whois_mock.get_keyset_by_handle.return_value = get_keyset()

            result = domain_to_dict(self.request, get_domain(keyset_handle='gazpacho'))

        self.assertEqual(result['fred_keyset']['links'][0]['value'], 'http://rdap.example/fred_keyset/gazpacho')

    def test_port43(self):
        with override_settings(RDAP_UNIX_WHOIS='whois.example.com'):
            result = domain_to_dict(self.request, get_domain())
        self.assertEqual(result['port43'], 'whois.example.com')

    def test_max_sig_life_absent(self):
        with patch.object(WHOIS, 'client', spec=('get_keyset_by_handle', )) as whois_mock:
            whois_mock.get_keyset_by_handle.return_value = get_keyset()
            with self.settings(RDAP_MAX_SIG_LIFE=None):
                result = domain_to_dict(self.request, get_domain(keyset_handle='gazpacho'))
        self.assertNotIn('maxSigLife', result['secureDNS'])

    def test_max_sig_life_present(self):
        with patch.object(WHOIS, 'client', spec=('get_keyset_by_handle', )) as whois_mock:
            whois_mock.get_keyset_by_handle.return_value = get_keyset()
            with self.settings(RDAP_MAX_SIG_LIFE=sentinel.max_sig_life):
                result = domain_to_dict(self.request, get_domain(keyset_handle='gazpacho'))
        self.assertEqual(result['secureDNS']['maxSigLife'], sentinel.max_sig_life)


@override_settings(ALLOWED_HOSTS=['rdap.example'], RDAP_UNIX_WHOIS=None)
class TestDeleteCandidateDomainToDict(SimpleTestCase):
    """Test `rdap.rdap_rest.domain.delete_candidate_domain_to_dict` function."""

    def setUp(self):
        self.request = RequestFactory(HTTP_HOST='rdap.example').get('/dummy/')

    def test_simple(self):
        result = delete_candidate_domain_to_dict(self.request, 'example.cz')
        data = {'objectClassName': 'domain',
                'rdapConformance': ['rdap_level_0', 'fred_version_0'],
                'handle': 'example.cz',
                'ldhName': 'example.cz',
                'links': [
                    {
                        'value': 'http://rdap.example/domain/example.cz',
                        'rel': 'self',
                        'href': 'http://rdap.example/domain/example.cz',
                        'type': 'application/rdap+json',
                    },
                ],
                'status': ['pending delete']}
        self.assertEqual(result, data)

    def test_port43(self):
        with override_settings(RDAP_UNIX_WHOIS='whois.example.com'):
            result = delete_candidate_domain_to_dict(self.request, 'example.cz')
        self.assertEqual(result['port43'], 'whois.example.com')


@override_settings(ALLOWED_HOSTS=['rdap.example'], RDAP_UNIX_WHOIS=None)
class TestContactToDict(SimpleTestCase):
    """Test `rdap.rdap_rest.domain.contact_to_dict` function."""

    def setUp(self):
        self.request = RequestFactory(HTTP_HOST='rdap.example').get('/dummy/')

    def test_simple(self):
        result = contact_to_dict(self.request, get_contact())
        self.assertEqual(result['links'][0]['value'], 'http://rdap.example/entity/KRYTEN')
        self.assertNotIn('port43', result)

    def test_port43(self):
        with override_settings(RDAP_UNIX_WHOIS='whois.example.com'):
            result = contact_to_dict(self.request, get_contact())
        self.assertEqual(result['port43'], 'whois.example.com')


@override_settings(ALLOWED_HOSTS=['rdap.example'], RDAP_UNIX_WHOIS=None)
class TestKeysetToDict(SimpleTestCase):
    """Test `rdap.rdap_rest.domain.keyset_to_dict` function."""

    def setUp(self):
        self.request = RequestFactory(HTTP_HOST='rdap.example').get('/dummy/')

    def test_simple(self):
        result = keyset_to_dict(self.request, get_keyset())
        self.assertEqual(result['links'][0]['value'], 'http://rdap.example/fred_keyset/gazpacho')
        self.assertNotIn('port43', result)

    def test_tech_contacts(self):
        result = keyset_to_dict(self.request, get_keyset(tech_contact_handles=['KOCHANSKI']))
        tech = result['entities'][1]
        self.assertEqual(tech['roles'], ['technical'])
        self.assertEqual(tech['links'][0]['value'], 'http://rdap.example/entity/KOCHANSKI')

    def test_port43(self):
        with override_settings(RDAP_UNIX_WHOIS='whois.example.com'):
            result = keyset_to_dict(self.request, get_keyset())
        self.assertEqual(result['port43'], 'whois.example.com')


@override_settings(ALLOWED_HOSTS=['rdap.example'])
class TestNameserverToDict(SimpleTestCase):
    """Test `rdap.rdap_rest.domain.nameserver_to_dict` function."""

    def setUp(self):
        self.request = RequestFactory(HTTP_HOST='rdap.example').get('/dummy/')

    def test_simple(self):
        nameserver = NameServer(fqdn='nameserver.example.cz', ip_addresses=[])
        result = nameserver_to_dict(self.request, nameserver)
        self.assertEqual(result['links'][0]['value'], 'http://rdap.example/nameserver/nameserver.example.cz')


@override_settings(ALLOWED_HOSTS=['rdap.example'], RDAP_UNIX_WHOIS=None)
class TestNssetToDict(SimpleTestCase):
    """Test `rdap.rdap_rest.domain.nsset_to_dict` function."""

    def setUp(self):
        self.request = RequestFactory(HTTP_HOST='rdap.example').get('/dummy/')

    def test_simple(self):
        result = nsset_to_dict(self.request, get_nsset())
        self.assertEqual(result['links'][0]['value'], 'http://rdap.example/fred_nsset/new-saturn')
        self.assertNotIn('port43', result)

    def test_tech_contacts(self):
        result = nsset_to_dict(self.request, get_nsset(tech_contact_handles=['KOCHANSKI']))
        tech = result['entities'][1]
        self.assertEqual(tech['roles'], ['technical'])
        self.assertEqual(tech['links'][0]['value'], 'http://rdap.example/entity/KOCHANSKI')

    def test_nameservers(self):
        nservers = [NameServer(fqdn='nameserver.example.cz', ip_addresses=[])]
        result = nsset_to_dict(self.request, get_nsset(nservers=nservers))
        self.assertEqual(result['nameservers'][0]['links'][0]['value'],
                         'http://rdap.example/nameserver/nameserver.example.cz')

    def test_port43(self):
        with override_settings(RDAP_UNIX_WHOIS='whois.example.com'):
            result = nsset_to_dict(self.request, get_nsset())
        self.assertEqual(result['port43'], 'whois.example.com')
