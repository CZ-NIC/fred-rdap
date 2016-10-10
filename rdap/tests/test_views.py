"""
Tests of RDAP views.
"""
import json
import os

from django.test import SimpleTestCase
from mock import call, patch
from omniORB.CORBA import TRANSIENT

from rdap.rdap_rest.whois import _INTERFACE


class TestObjectView(SimpleTestCase):
    """
    Test `ObjectView` class.
    """
    def setUp(self):
        patcher = patch('rdap.rdap_rest.whois._WHOIS')
        self.addCleanup(patcher.stop)
        self.whois_mock = patcher.start()

        log_patcher = patch('rdap.views.LOGGER')
        self.addCleanup(log_patcher.stop)
        self.logger_mock = log_patcher.start()

    def get_contact(self):
        address = _INTERFACE.Whois.PlaceAddress('', '', '', '', '', '', '')
        ident = _INTERFACE.Whois.ContactIdentification('OP', '')
        return _INTERFACE.Whois.Contact('kryten',
                                        _INTERFACE.Whois.DisclosableString('', True),
                                        _INTERFACE.Whois.DisclosableString('', True),
                                        _INTERFACE.Whois.DisclosablePlaceAddress(address, True),
                                        _INTERFACE.Whois.DisclosableString('', True),
                                        _INTERFACE.Whois.DisclosableString('', True),
                                        _INTERFACE.Whois.DisclosableString('', True),
                                        _INTERFACE.Whois.DisclosableString('', True),
                                        _INTERFACE.Whois.DisclosableString('', True),
                                        _INTERFACE.Whois.DisclosableContactIdentification(ident, True),
                                        '',
                                        '',
                                        _INTERFACE.DateTime(_INTERFACE.Date(6, 9, 1988), 20, 0, 0),
                                        None,
                                        None,
                                        [])

    def test_entity(self):
        self.whois_mock.get_contact_by_handle.return_value = self.get_contact()
        response = self.client.get('/entity/kryten')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        self.assertEqual(response['Access-Control-Allow-Origin'], '*')
        result = json.loads(response.content)
        self.assertEqual(result['objectClassName'], 'entity')
        self.assertEqual(result['handle'], 'kryten')

        # Check logger
        calls = [call.create_request('127.0.0.1', 'RDAP', 'EntityLookup', properties=[('handle', 'kryten')]),
                 call.create_request().close(properties=[])]
        self.assertEqual(self.logger_mock.mock_calls, calls)
        self.assertEqual(self.logger_mock.create_request.return_value.result, 'Ok')

    def test_disclaimer(self):
        self.whois_mock.get_contact_by_handle.return_value = self.get_contact()
        with self.settings(DISCLAIMER_FILE=os.path.join(os.path.dirname(__file__), 'data', 'disclaimer.txt')):
            response = self.client.get('/entity/kryten')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        self.assertEqual(response['Access-Control-Allow-Origin'], '*')
        result = json.loads(response.content)
        self.assertEqual(result['objectClassName'], 'entity')
        self.assertEqual(result['handle'], 'kryten')
        self.assertIn({'title': 'Disclaimer', 'description': ['Quagaars!\n']}, result['notices'])

    def test_entity_not_found(self):
        self.whois_mock.get_contact_by_handle.side_effect = _INTERFACE.Whois.OBJECT_NOT_FOUND
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
        self.whois_mock.get_contact_by_handle.side_effect = _INTERFACE.Whois.INVALID_HANDLE
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
        self.whois_mock.get_contact_by_handle.side_effect = TRANSIENT
        with self.assertRaises(TRANSIENT):
            self.client.get('/entity/kryten')

        # Check logger
        calls = [call.create_request('127.0.0.1', 'RDAP', 'EntityLookup', properties=[('handle', 'kryten')]),
                 call.create_request().close(properties=[('error', 'TRANSIENT')])]
        self.assertEqual(self.logger_mock.mock_calls, calls)


class TestFqdnObjectView(SimpleTestCase):
    """
    Test `FqdnObjectView` class.
    """
    def setUp(self):
        patcher = patch('rdap.rdap_rest.whois._WHOIS')
        self.addCleanup(patcher.stop)
        self.whois_mock = patcher.start()

        log_patcher = patch('rdap.views.LOGGER')
        self.addCleanup(log_patcher.stop)
        self.logger_mock = log_patcher.start()

    def test_nameserver(self):
        self.whois_mock.get_nameserver_by_fqdn.return_value = _INTERFACE.Whois.NameServer('holly', [])
        response = self.client.get('/nameserver/holly')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        self.assertEqual(response['Access-Control-Allow-Origin'], '*')
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
    def test_get(self):
        response = self.client.get('/help')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        self.assertEqual(response['Access-Control-Allow-Origin'], '*')
        data = {
            "rdapConformance": ["rdap_level_0", "fred_version_0"],
            "notices": [{"title": "Help", "description": ["No help."]}],
        }
        self.assertJSONEqual(response.content, data)


class TestUnsupportedView(SimpleTestCase):
    """
    Test `UnsupportedView` class.
    """
    def test_unsupported_view(self):
        response = self.client.get('/autnum/foo')

        self.assertEqual(response.status_code, 501)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        self.assertEqual(response.content, '')
