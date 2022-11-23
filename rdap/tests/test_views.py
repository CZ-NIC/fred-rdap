#
# Copyright (C) 2016-2022  CZ.NIC, z. s. p. o.
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
import json
from unittest.mock import patch

from django.test import Client, SimpleTestCase
from fred_idl.Registry.Whois import INVALID_LABEL, OBJECT_NOT_FOUND, NameServer
from grill.utils import TestLogEntry, TestLoggerClient
from omniORB.CORBA import TRANSIENT
from regal import Contact
from regal.exceptions import ContactDoesNotExist

from rdap.constants import LOGGER_SERVICE, LogEntryType, LogResult
from rdap.utils.corba import WHOIS


class EnforcingCsrfClient(Client):
    """
    Test client which enforces CSRF checks.
    """

    def __init__(self, **defaults):
        super(EnforcingCsrfClient, self).__init__(enforce_csrf_checks=True, **defaults)


class TestObjectView(SimpleTestCase):
    """
    Test `ObjectView` class.
    """
    client_class = EnforcingCsrfClient

    def setUp(self):
        patcher = patch.object(WHOIS, 'client', spec=('get_domain_by_handle', ))
        self.addCleanup(patcher.stop)
        patcher.start()

        self.test_logger = TestLoggerClient()
        log_patcher = patch('rdap.views.LOGGER.client', new=self.test_logger)
        self.addCleanup(log_patcher.stop)
        log_patcher.start()

    def test_entity(self):
        patcher = patch('rdap.rdap_rest.whois.CONTACT_CLIENT',
                        spec=('get_contact_info', 'get_contact_id', 'get_contact_state'))
        with patcher as contact_mock:
            contact = Contact(contact_id='2X4B', contact_handle='kryten', sponsoring_registrar='HOLLY')
            contact_mock.get_contact_id.return_value = '2X4B'
            contact_mock.get_contact_info.return_value = contact
            contact_mock.get_contact_state.return_value = {}

            with patch('rdap.rdap_rest.entity.CONTACT_CLIENT', new=contact_mock):

                response = self.client.get('/entity/kryten')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        result = json.loads(response.content.decode())
        self.assertEqual(result['objectClassName'], 'entity')
        self.assertEqual(result['handle'], 'kryten')

        # Check logger
        log_entry = TestLogEntry(LOGGER_SERVICE, LogEntryType.ENTITY_LOOKUP, LogResult.SUCCESS, source_ip='127.0.0.1',
                                 input_properties={'handle': 'kryten'})
        self.assertEqual(self.test_logger.mock.mock_calls, log_entry.get_calls())

    def test_disclaimer(self):
        patcher = patch('rdap.rdap_rest.whois.CONTACT_CLIENT',
                        spec=('get_contact_info', 'get_contact_id', 'get_contact_state'))
        with patcher as contact_mock:
            contact = Contact(contact_id='2X4B', contact_handle='kryten', sponsoring_registrar='HOLLY')
            contact_mock.get_contact_id.return_value = '2X4B'
            contact_mock.get_contact_info.return_value = contact
            contact_mock.get_contact_state.return_value = {}

            with patch('rdap.rdap_rest.entity.CONTACT_CLIENT', new=contact_mock):
                with self.settings(RDAP_DISCLAIMER=['Quagaars!']):
                    response = self.client.get('/entity/kryten')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        result = json.loads(response.content.decode())
        self.assertEqual(result['objectClassName'], 'entity')
        self.assertEqual(result['handle'], 'kryten')
        self.assertIn({'title': 'Disclaimer', 'description': ['Quagaars!']}, result['notices'])

    def test_entity_not_found(self):
        patcher = patch('rdap.rdap_rest.whois.CONTACT_CLIENT', spec=('get_contact_id', 'get_contact_info'))
        with patcher as contact_mock:
            contact_mock.get_contact_id.side_effect = ContactDoesNotExist

            response = self.client.get('/entity/kryten')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        self.assertEqual(response.content, b'')

        # Check logger
        log_entry = TestLogEntry(LOGGER_SERVICE, LogEntryType.ENTITY_LOOKUP, LogResult.NOT_FOUND, source_ip='127.0.0.1',
                                 input_properties={'handle': 'kryten'})
        self.assertEqual(self.test_logger.mock.mock_calls, log_entry.get_calls())

    def test_entity_exception(self):
        patcher = patch('rdap.rdap_rest.whois.CONTACT_CLIENT', spec=('get_contact_id', 'get_contact_info'))
        with patcher as contact_mock:
            contact_mock.get_contact_id.side_effect = Exception('Gazpacho!')

            with self.assertRaisesRegexp(Exception, 'Gazpacho!'):
                self.client.get('/entity/kryten')

        # Check logger
        log_entry = TestLogEntry(LOGGER_SERVICE, LogEntryType.ENTITY_LOOKUP, LogResult.INTERNAL_SERVER_ERROR,
                                 source_ip='127.0.0.1', input_properties={'handle': 'kryten'},
                                 properties={'error': 'Exception'})
        self.assertEqual(self.test_logger.mock.mock_calls, log_entry.get_calls())

    def test_domain_not_found(self):
        WHOIS.get_domain_by_handle.side_effect = OBJECT_NOT_FOUND
        response = self.client.get('/domain/example.org')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        self.assertEqual(response.content, b'')

        # Check logger
        log_entry = TestLogEntry(LOGGER_SERVICE, LogEntryType.DOMAIN_LOOKUP, LogResult.NOT_FOUND, source_ip='127.0.0.1',
                                 input_properties={'handle': 'example.org'})
        self.assertEqual(self.test_logger.mock.mock_calls, log_entry.get_calls())

    def test_domain_invalid_handle(self):
        WHOIS.get_domain_by_handle.side_effect = INVALID_LABEL
        response = self.client.get('/domain/example.org')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        self.assertEqual(response.content, b'')

        # Check logger
        log_entry = TestLogEntry(LOGGER_SERVICE, LogEntryType.DOMAIN_LOOKUP, LogResult.BAD_REQUEST,
                                 source_ip='127.0.0.1', input_properties={'handle': 'example.org'})
        self.assertEqual(self.test_logger.mock.mock_calls, log_entry.get_calls())

    def test_domain_exception(self):
        WHOIS.get_domain_by_handle.side_effect = TRANSIENT
        with self.assertRaises(TRANSIENT):
            self.client.get('/domain/example.org')

        # Check logger
        log_entry = TestLogEntry(LOGGER_SERVICE, LogEntryType.DOMAIN_LOOKUP, LogResult.INTERNAL_SERVER_ERROR,
                                 source_ip='127.0.0.1', input_properties={'handle': 'example.org'},
                                 properties={'error': 'TRANSIENT'})
        self.assertEqual(self.test_logger.mock.mock_calls, log_entry.get_calls())

    def test_post(self):
        # Test POST returns `Method Not Allowed` response instead of CSRF check failure.
        response = self.client.post('/entity/kryten', {})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, b'')


class TestFqdnObjectView(SimpleTestCase):
    """
    Test `FqdnObjectView` class.
    """

    def setUp(self):
        patcher = patch.object(WHOIS, 'client', spec=('get_nameserver_by_fqdn', ))
        self.addCleanup(patcher.stop)
        patcher.start()

        self.test_logger = TestLoggerClient()
        log_patcher = patch('rdap.views.LOGGER.client', new=self.test_logger)
        self.addCleanup(log_patcher.stop)
        log_patcher.start()

    def test_nameserver(self):
        WHOIS.get_nameserver_by_fqdn.return_value = NameServer('holly', [])
        response = self.client.get('/nameserver/holly')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        result = json.loads(response.content.decode())
        self.assertEqual(result['objectClassName'], 'nameserver')
        self.assertEqual(result['handle'], 'holly')

        # Check logger
        log_entry = TestLogEntry(LOGGER_SERVICE, LogEntryType.NAMESERVER_LOOKUP, LogResult.SUCCESS,
                                 source_ip='127.0.0.1', input_properties={'handle': 'holly'})
        self.assertEqual(self.test_logger.mock.mock_calls, log_entry.get_calls())

    def test_nameserver_invalid_fqdn(self):
        response = self.client.get('/nameserver/-invalid')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        self.assertEqual(response.content, b'')

        # Check logger
        self.assertEqual(self.test_logger.mock.mock_calls, [])


class TestHelpView(SimpleTestCase):
    """
    Test `HelpView` class.
    """
    client_class = EnforcingCsrfClient

    def test_get(self):
        response = self.client.get('/help')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        help_text = 'See the API reference: https://fred.nic.cz/documentation/html/RDAPReference'
        data = {
            "rdapConformance": ["rdap_level_0", "fred_version_0"],
            "notices": [{"title": "Help", "description": [help_text]}],
        }
        self.assertJSONEqual(response.content.decode(), data)

    def test_post(self):
        # Test POST returns `Method Not Allowed` response instead of CSRF check failure.
        response = self.client.post('/entity/kryten', {})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, b'')


class TestUnsupportedView(SimpleTestCase):
    """
    Test `UnsupportedView` class.
    """
    client_class = EnforcingCsrfClient

    def test_unsupported_view(self):
        response = self.client.get('/autnum/foo')

        self.assertEqual(response.status_code, 501)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        self.assertEqual(response.content, b'')

    def test_post(self):
        # Test POST returns `Method Not Allowed` response instead of CSRF check failure.
        response = self.client.post('/entity/kryten', {})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, b'')
