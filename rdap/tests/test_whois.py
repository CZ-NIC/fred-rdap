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
from unittest.mock import call, patch

from django.test import RequestFactory, SimpleTestCase
from fred_idl.Registry.Whois import OBJECT_DELETE_CANDIDATE
from regal import Contact
from regal.exceptions import ContactDoesNotExist

from rdap.rdap_rest.whois import get_contact_by_handle, get_domain_by_handle
from rdap.utils.corba import WHOIS


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


class TestGetDomainByHandle(SimpleTestCase):
    def setUp(self):
        patcher = patch.object(WHOIS, 'client', spec=('get_domain_by_handle', ))
        self.addCleanup(patcher.stop)
        patcher.start()

    def test_domain_delete_candidate(self):
        WHOIS.get_domain_by_handle.side_effect = OBJECT_DELETE_CANDIDATE
        request = RequestFactory().get('/dummy/')

        response = get_domain_by_handle(request, 'test.example')

        self.assertEqual(response['handle'], 'test.example')
        self.assertEqual(response['objectClassName'], 'domain')
        self.assertEqual(response['status'], ['pending delete'])

        # Check corba calls
        calls = [call.get_domain_by_handle('test.example')]
        self.assertEqual(WHOIS.client.mock_calls, calls)
