#
# Copyright (C) 2019-2022  CZ.NIC, z. s. p. o.
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
#
from datetime import datetime, timezone
from unittest.mock import call, patch

from django.test import RequestFactory, SimpleTestCase, override_settings
from regal import Contact, Domain, Keyset, Nsset, ObjectEvent, ObjectEvents
from regal.exceptions import (ContactDoesNotExist, DomainDoesNotExist, KeysetDoesNotExist, NssetDoesNotExist,
                              ObjectDoesNotExist)

from rdap.rdap_rest.whois import (get_contact_by_handle, get_domain_by_handle, get_keyset_by_handle,
                                  get_nameserver_by_handle, get_nsset_by_handle)


class TestGetContactByHandle(SimpleTestCase):
    def setUp(self):
        patcher = patch('rdap.rdap_rest.whois.CONTACT_CLIENT', spec=('get_contact_info', 'get_contact_id'))
        self.addCleanup(patcher.stop)
        self.contact_mock = patcher.start()

    def test_contact(self):
        contact = Contact(contact_id='2X4B', contact_handle='KRYTEN', sponsoring_registrar='HOLLY')
        self.contact_mock.get_contact_id.return_value = '2X4B'
        self.contact_mock.get_contact_info.return_value = contact
        request = RequestFactory().get('/dummy/')

        with patch('rdap.rdap_rest.entity.CONTACT_CLIENT') as entity_mock:
            entity_mock.get_contact_state.return_value = {}
            response = get_contact_by_handle(request, 'KRYTEN')

        self.assertEqual(response['handle'], 'KRYTEN')
        self.assertEqual(response['objectClassName'], 'entity')
        calls = [call.get_contact_id('KRYTEN'), call.get_contact_info('2X4B')]
        self.assertEqual(self.contact_mock.mock_calls, calls)

    def test_contact_not_found(self):
        self.contact_mock.get_contact_id.return_value = '2X4B'
        self.contact_mock.get_contact_info.side_effect = ContactDoesNotExist
        request = RequestFactory().get('/dummy/')

        with self.assertRaises(ContactDoesNotExist):
            get_contact_by_handle(request, 'KRYTEN')

        calls = [call.get_contact_id('KRYTEN'), call.get_contact_info('2X4B')]
        self.assertEqual(self.contact_mock.mock_calls, calls)

    def test_contact_id_not_found(self):
        self.contact_mock.get_contact_id.side_effect = ContactDoesNotExist
        request = RequestFactory().get('/dummy/')

        with self.assertRaises(ContactDoesNotExist):
            get_contact_by_handle(request, 'KRYTEN')

        calls = [call.get_contact_id('KRYTEN')]
        self.assertEqual(self.contact_mock.mock_calls, calls)


@override_settings(USE_TZ=True)
class TestGetDomainByHandle(SimpleTestCase):
    def setUp(self):
        patcher = patch('rdap.rdap_rest.whois.DOMAIN_CLIENT', spec=('get_domain_info', 'get_domain_id'))
        self.addCleanup(patcher.stop)
        self.domain_mock = patcher.start()
        patcher = patch('rdap.rdap_rest.domain.CONTACT_CLIENT', spec=('get_contact_info', ))
        self.addCleanup(patcher.stop)
        self.contact_mock = patcher.start()
        self.contact_mock.get_contact_info.return_value = Contact(contact_id='2X4B', contact_handle='KRYTEN')

    def test_domain(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'))
        domain = Domain(domain_id='2X4B', fqdn='example.org', sponsoring_registrar='HOLLY', events=events,
                        registrant='KRYTEN', expires_at=datetime(1999, 4, 5, tzinfo=timezone.utc))
        self.domain_mock.get_domain_id.return_value = '2X4B'
        self.domain_mock.get_domain_info.return_value = domain
        request = RequestFactory().get('/dummy/')

        with patch('rdap.rdap_rest.domain.DOMAIN_CLIENT') as entity_mock:
            entity_mock.get_domain_state.return_value = {}
            response = get_domain_by_handle(request, 'example.org')

        self.assertEqual(response['handle'], 'example.org')
        self.assertEqual(response['objectClassName'], 'domain')
        calls = [call.get_domain_id('example.org'), call.get_domain_info('2X4B')]
        self.assertEqual(self.domain_mock.mock_calls, calls)

    def test_domain_not_found(self):
        self.domain_mock.get_domain_id.return_value = '2X4B'
        self.domain_mock.get_domain_info.side_effect = DomainDoesNotExist
        request = RequestFactory().get('/dummy/')

        with self.assertRaises(DomainDoesNotExist):
            get_domain_by_handle(request, 'example.org')

        calls = [call.get_domain_id('example.org'), call.get_domain_info('2X4B')]
        self.assertEqual(self.domain_mock.mock_calls, calls)

    def test_domain_id_not_found(self):
        self.domain_mock.get_domain_id.side_effect = DomainDoesNotExist
        request = RequestFactory().get('/dummy/')

        with self.assertRaises(DomainDoesNotExist):
            get_domain_by_handle(request, 'example.org')

        calls = [call.get_domain_id('example.org')]
        self.assertEqual(self.domain_mock.mock_calls, calls)


@override_settings(USE_TZ=True)
class TestGetKeysetByHandle(SimpleTestCase):
    def setUp(self):
        patcher = patch('rdap.rdap_rest.whois.KEYSET_CLIENT', spec=('get_keyset_info', 'get_keyset_id'))
        self.addCleanup(patcher.stop)
        self.keyset_mock = patcher.start()

    def test_keyset(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'))
        keyset = Keyset(keyset_id='2X4B', keyset_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events)
        self.keyset_mock.get_keyset_id.return_value = '2X4B'
        self.keyset_mock.get_keyset_info.return_value = keyset
        request = RequestFactory().get('/dummy/')

        with patch('rdap.rdap_rest.keyset.KEYSET_CLIENT') as entity_mock:
            entity_mock.get_keyset_state.return_value = {}
            response = get_keyset_by_handle(request, 'KRYTEN')

        self.assertEqual(response['handle'], 'KRYTEN')
        self.assertEqual(response['objectClassName'], 'fred_keyset')
        calls = [call.get_keyset_id('KRYTEN'), call.get_keyset_info('2X4B')]
        self.assertEqual(self.keyset_mock.mock_calls, calls)

    def test_keyset_not_found(self):
        self.keyset_mock.get_keyset_id.return_value = '2X4B'
        self.keyset_mock.get_keyset_info.side_effect = KeysetDoesNotExist
        request = RequestFactory().get('/dummy/')

        with self.assertRaises(KeysetDoesNotExist):
            get_keyset_by_handle(request, 'KRYTEN')

        calls = [call.get_keyset_id('KRYTEN'), call.get_keyset_info('2X4B')]
        self.assertEqual(self.keyset_mock.mock_calls, calls)

    def test_keyset_id_not_found(self):
        self.keyset_mock.get_keyset_id.side_effect = KeysetDoesNotExist
        request = RequestFactory().get('/dummy/')

        with self.assertRaises(KeysetDoesNotExist):
            get_keyset_by_handle(request, 'KRYTEN')

        calls = [call.get_keyset_id('KRYTEN')]
        self.assertEqual(self.keyset_mock.mock_calls, calls)


class TestGetNameserverByHandle(SimpleTestCase):
    def setUp(self):
        patcher = patch('rdap.rdap_rest.whois.NSSET_CLIENT', spec=('check_dns_host', ))
        self.addCleanup(patcher.stop)
        self.nameserver_mock = patcher.start()

    def test_nameserver(self):
        self.nameserver_mock.check_dns_host.return_value = True
        request = RequestFactory().get('/dummy/')

        response = get_nameserver_by_handle(request, 'ns.example.org')

        self.assertEqual(response['handle'], 'ns.example.org')
        self.assertEqual(response['objectClassName'], 'nameserver')
        calls = [call.check_dns_host('ns.example.org')]
        self.assertEqual(self.nameserver_mock.mock_calls, calls)

    def test_nameserver_not_found(self):
        self.nameserver_mock.check_dns_host.return_value = False
        request = RequestFactory().get('/dummy/')

        with self.assertRaises(ObjectDoesNotExist):
            get_nameserver_by_handle(request, 'ns.example.org')

        calls = [call.check_dns_host('ns.example.org')]
        self.assertEqual(self.nameserver_mock.mock_calls, calls)


@override_settings(USE_TZ=True)
class TestGetNssetByHandle(SimpleTestCase):
    def setUp(self):
        patcher = patch('rdap.rdap_rest.whois.NSSET_CLIENT', spec=('get_nsset_info', 'get_nsset_id'))
        self.addCleanup(patcher.stop)
        self.nsset_mock = patcher.start()

    def test_nsset(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'))
        nsset = Nsset(nsset_id='2X4B', nsset_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events)
        self.nsset_mock.get_nsset_id.return_value = '2X4B'
        self.nsset_mock.get_nsset_info.return_value = nsset
        request = RequestFactory().get('/dummy/')

        with patch('rdap.rdap_rest.nsset.NSSET_CLIENT') as entity_mock:
            entity_mock.get_nsset_state.return_value = {}
            response = get_nsset_by_handle(request, 'KRYTEN')

        self.assertEqual(response['handle'], 'KRYTEN')
        self.assertEqual(response['objectClassName'], 'fred_nsset')
        calls = [call.get_nsset_id('KRYTEN'), call.get_nsset_info('2X4B')]
        self.assertEqual(self.nsset_mock.mock_calls, calls)

    def test_nsset_not_found(self):
        self.nsset_mock.get_nsset_id.return_value = '2X4B'
        self.nsset_mock.get_nsset_info.side_effect = NssetDoesNotExist
        request = RequestFactory().get('/dummy/')

        with self.assertRaises(NssetDoesNotExist):
            get_nsset_by_handle(request, 'KRYTEN')

        calls = [call.get_nsset_id('KRYTEN'), call.get_nsset_info('2X4B')]
        self.assertEqual(self.nsset_mock.mock_calls, calls)

    def test_nsset_id_not_found(self):
        self.nsset_mock.get_nsset_id.side_effect = NssetDoesNotExist
        request = RequestFactory().get('/dummy/')

        with self.assertRaises(NssetDoesNotExist):
            get_nsset_by_handle(request, 'KRYTEN')

        calls = [call.get_nsset_id('KRYTEN')]
        self.assertEqual(self.nsset_mock.mock_calls, calls)
