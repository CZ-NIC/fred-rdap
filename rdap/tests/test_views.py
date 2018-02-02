"""
Tests of RDAP views.
"""
import json
import os

from django.test import Client, SimpleTestCase
from fred_idl.Registry import Date, DateTime
from fred_idl.Registry.Whois import INVALID_HANDLE, OBJECT_NOT_FOUND, Contact, ContactIdentification, \
    DisclosableContactIdentification, DisclosablePlaceAddress, DisclosableString, NameServer, PlaceAddress
from mock import call, patch
from omniORB.CORBA import TRANSIENT

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
        patcher = patch.object(WHOIS, 'client', spec=('get_contact_by_handle', ))
        self.addCleanup(patcher.stop)
        patcher.start()

        log_patcher = patch('rdap.views.LOGGER')
        self.addCleanup(log_patcher.stop)
        self.logger_mock = log_patcher.start()

    def get_contact(self):
        address = PlaceAddress('', '', '', '', '', '', '')
        ident = ContactIdentification('OP', '')
        return Contact(
            'kryten',
            DisclosableString('', True),
            DisclosableString('', True),
            DisclosablePlaceAddress(address, True),
            DisclosableString('', True),
            DisclosableString('', True),
            DisclosableString('', True),
            DisclosableString('', True),
            DisclosableString('', True),
            DisclosableContactIdentification(ident, True),
            '',
            '',
            DateTime(Date(6, 9, 1988), 20, 0, 0),
            None,
            None,
            [])

    def test_entity(self):
        WHOIS.get_contact_by_handle.return_value = self.get_contact()
        response = self.client.get('/entity/kryten')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        result = json.loads(response.content)
        self.assertEqual(result['objectClassName'], 'entity')
        self.assertEqual(result['handle'], 'kryten')

        # Check logger
        calls = [call.create_request('127.0.0.1', 'RDAP', 'EntityLookup', properties=[('handle', 'kryten')]),
                 call.create_request().close(properties=[])]
        self.assertEqual(self.logger_mock.mock_calls, calls)
        self.assertEqual(self.logger_mock.create_request.return_value.result, 'Ok')

    def test_disclaimer(self):
        WHOIS.get_contact_by_handle.return_value = self.get_contact()
        with self.settings(DISCLAIMER_FILE=os.path.join(os.path.dirname(__file__), 'data', 'disclaimer.txt')):
            response = self.client.get('/entity/kryten')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        result = json.loads(response.content)
        self.assertEqual(result['objectClassName'], 'entity')
        self.assertEqual(result['handle'], 'kryten')
        self.assertIn({'title': 'Disclaimer', 'description': ['Quagaars!\n']}, result['notices'])

    def test_entity_not_found(self):
        WHOIS.get_contact_by_handle.side_effect = OBJECT_NOT_FOUND
        response = self.client.get('/entity/kryten')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        self.assertEqual(response.content, '')

        # Check logger
        calls = [call.create_request('127.0.0.1', 'RDAP', 'EntityLookup', properties=[('handle', 'kryten')]),
                 call.create_request().close(properties=[])]
        self.assertEqual(self.logger_mock.mock_calls, calls)
        self.assertEqual(self.logger_mock.create_request.return_value.result, 'NotFound')

    def test_entity_invalid_handle(self):
        WHOIS.get_contact_by_handle.side_effect = INVALID_HANDLE
        response = self.client.get('/entity/kryten')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        self.assertEqual(response.content, '')

        # Check logger
        calls = [call.create_request('127.0.0.1', 'RDAP', 'EntityLookup', properties=[('handle', 'kryten')]),
                 call.create_request().close(properties=[])]
        self.assertEqual(self.logger_mock.mock_calls, calls)
        self.assertEqual(self.logger_mock.create_request.return_value.result, 'BadRequest')

    def test_entity_exception(self):
        WHOIS.get_contact_by_handle.side_effect = TRANSIENT
        with self.assertRaises(TRANSIENT):
            self.client.get('/entity/kryten')

        # Check logger
        calls = [call.create_request('127.0.0.1', 'RDAP', 'EntityLookup', properties=[('handle', 'kryten')]),
                 call.create_request().close(properties=[('error', 'TRANSIENT')])]
        self.assertEqual(self.logger_mock.mock_calls, calls)

    def test_post(self):
        # Test POST returns `Method Not Allowed` response instead of CSRF check failure.
        response = self.client.post('/entity/kryten', {})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, '')


class TestFqdnObjectView(SimpleTestCase):
    """
    Test `FqdnObjectView` class.
    """
    def setUp(self):
        patcher = patch.object(WHOIS, 'client', spec=('get_nameserver_by_fqdn', ))
        self.addCleanup(patcher.stop)
        patcher.start()

        log_patcher = patch('rdap.views.LOGGER')
        self.addCleanup(log_patcher.stop)
        self.logger_mock = log_patcher.start()

    def test_nameserver(self):
        WHOIS.get_nameserver_by_fqdn.return_value = NameServer('holly', [])
        response = self.client.get('/nameserver/holly')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        result = json.loads(response.content)
        self.assertEqual(result['objectClassName'], 'nameserver')
        self.assertEqual(result['handle'], 'holly')

        # Check logger
        calls = [call.create_request('127.0.0.1', 'RDAP', 'NameserverLookup', properties=[('handle', 'holly')]),
                 call.create_request().close(properties=[])]
        self.assertEqual(self.logger_mock.mock_calls, calls)
        self.assertEqual(self.logger_mock.create_request.return_value.result, 'Ok')

    def test_nameserver_invalid_fqdn(self):
        response = self.client.get(u'/nameserver/-invalid')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        self.assertEqual(response.content, '')

        # Check logger
        self.assertEqual(self.logger_mock.mock_calls, [])


class TestHelpView(SimpleTestCase):
    """
    Test `HelpView` class.
    """
    client_class = EnforcingCsrfClient

    def test_get(self):
        response = self.client.get('/help')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        data = {
            "rdapConformance": ["rdap_level_0", "fred_version_0"],
            "notices": [{"title": "Help", "description": ["No help."]}],
        }
        self.assertJSONEqual(response.content, data)

    def test_post(self):
        # Test POST returns `Method Not Allowed` response instead of CSRF check failure.
        response = self.client.post('/entity/kryten', {})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, '')


class TestUnsupportedView(SimpleTestCase):
    """
    Test `UnsupportedView` class.
    """
    client_class = EnforcingCsrfClient

    def test_unsupported_view(self):
        response = self.client.get('/autnum/foo')

        self.assertEqual(response.status_code, 501)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        self.assertEqual(response.content, '')

    def test_post(self):
        # Test POST returns `Method Not Allowed` response instead of CSRF check failure.
        response = self.client.post('/entity/kryten', {})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, '')
