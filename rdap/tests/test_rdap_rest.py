#
# Copyright (C) 2017-2022  CZ.NIC, z. s. p. o.
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
"""Tests for `rdap.rdap_rest` package."""
from datetime import date, datetime, timezone
from typing import Any, Dict, List
from unittest.mock import patch, sentinel

from django.test import RequestFactory, SimpleTestCase, override_settings
from fred_idl.Registry.Whois import Domain, KeySet, NameServer, NSSet
from regal import Address, Contact, ObjectEvent, ObjectEvents

from rdap.constants import ObjectStatus
from rdap.rdap_rest.domain import delete_candidate_domain_to_dict, domain_to_dict
from rdap.rdap_rest.entity import contact_to_dict
from rdap.rdap_rest.keyset import keyset_to_dict
from rdap.rdap_rest.nameserver import nameserver_to_dict
from rdap.rdap_rest.nsset import nsset_to_dict
from rdap.rdap_rest.rdap_utils import ObjectClassName
from rdap.utils.corba import WHOIS


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


@override_settings(ALLOWED_HOSTS=['rdap.example'], RDAP_UNIX_WHOIS=None, USE_TZ=True)
class TestContactToDict(SimpleTestCase):
    """Test `rdap.rdap_rest.domain.contact_to_dict` function."""

    def setUp(self):
        self.request = RequestFactory(HTTP_HOST='rdap.example').get('/dummy/')

        patcher = patch('rdap.rdap_rest.entity.CONTACT_CLIENT', spec=('get_contact_state', ))
        self.addCleanup(patcher.stop)
        self.contact_mock = patcher.start()

    def _test(self, contact: Contact, states: Dict[str, bool], data: Dict[str, Any]) -> None:
        self.contact_mock.get_contact_state.return_value = states

        result = contact_to_dict(contact, self.request)

        link = {'value': 'http://rdap.example/entity/KRYTEN', 'rel': 'self',
                'href': 'http://rdap.example/entity/KRYTEN', 'type': 'application/rdap+json'}
        defaults = {
            'rdapConformance': ["rdap_level_0"],
            'objectClassName': ObjectClassName.ENTITY,
            'handle': 'KRYTEN',
            'links': [link],
            'entities': [{'objectClassName': ObjectClassName.ENTITY, 'handle': 'HOLLY', 'roles': ['registrar']}],
        }
        self.assertEqual(result, dict(defaults, **data))

    def _test_unlinked(self, states: Dict[str, bool]) -> None:
        contact = Contact(contact_id='2X4B', contact_handle='KRYTEN', sponsoring_registrar='HOLLY')
        data = {'remarks': [{"description": ["Omitting data because contact is not linked to any registry object."]}]}
        self._test(contact, states, data)

    def test_unlinked_missing(self):
        self._test_unlinked({})

    def test_unlinked_false(self):
        self._test_unlinked({ObjectStatus.LINKED: False})

    def _test_linked(self, contact_kwargs: Dict[str, Any], vcard: List[List[Any]]) -> None:
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'))
        contact = Contact(contact_id='2X4B', contact_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events,
                          **contact_kwargs)

        events_data = [
            {'eventAction': 'registration', 'eventDate': '1988-09-06T00:00:00+00:00', 'eventActor': 'DIVADROID'}]
        data = {
            'vcardArray': ['vcard', vcard],
            'events': events_data,
            'status': ['associated'],
        }
        self._test(contact, {ObjectStatus.LINKED: True}, data)

    def test_linked_simple(self):
        self._test_linked({}, [["version", {}, "text", "4.0"]])

    def test_name_publish(self):
        vcard = [["version", {}, "text", "4.0"], ['fn', {}, 'text', 'Kryten']]
        self._test_linked({'name': 'Kryten', 'publish': {'name': True}}, vcard)

    def test_name_unpublish(self):
        vcard = [["version", {}, "text", "4.0"]]
        self._test_linked({'name': 'Kryten', 'publish': {'name': False}}, vcard)

    def test_name_empty(self):
        vcard = [["version", {}, "text", "4.0"]]
        self._test_linked({'name': '', 'publish': {'name': True}}, vcard)

    def test_organization_publish(self):
        vcard = [["version", {}, "text", "4.0"], ['org', {}, 'text', 'JMC']]
        self._test_linked({'organization': 'JMC', 'publish': {'organization': True}}, vcard)

    def test_organization_unpublish(self):
        vcard = [["version", {}, "text", "4.0"]]
        self._test_linked({'organization': 'JMC', 'publish': {'organization': False}}, vcard)

    def test_organization_empty(self):
        vcard = [["version", {}, "text", "4.0"]]
        self._test_linked({'organization': '', 'publish': {'organization': True}}, vcard)

    def test_place_publish(self):
        address = Address(street=['Deck 16'], city='Red Dwarf', state_or_province='Deep Space', postal_code='JMC',
                          country_code='JU')
        vcard = [["version", {}, "text", "4.0"],
                 ['adr', {'type': ''}, 'text', ['', 'Deck 16', '', '', 'Red Dwarf', 'Deep Space', 'JMC', 'JU']]]
        self._test_linked({'place': address, 'publish': {'place': True}}, vcard)

    def test_place_unpublish(self):
        address = Address(street=['Deck 16'], city='Red Dwarf', state_or_province='Deep Space', postal_code='JMC',
                          country_code='JU')
        vcard = [["version", {}, "text", "4.0"]]
        self._test_linked({'place': address, 'publish': {'place': False}}, vcard)

    def test_place_empty(self):
        vcard = [["version", {}, "text", "4.0"]]
        self._test_linked({'place': None, 'publish': {'place': True}}, vcard)

    def test_telephone_publish(self):
        vcard = [["version", {}, "text", "4.0"], ['tel', {'type': ['voice']}, 'uri', 'tel:+1.234']]
        self._test_linked({'telephone': '+1.234', 'publish': {'telephone': True}}, vcard)

    def test_telephone_unpublish(self):
        vcard = [["version", {}, "text", "4.0"]]
        self._test_linked({'telephone': '+1.234', 'publish': {'telephone': False}}, vcard)

    def test_telephone_empty(self):
        vcard = [["version", {}, "text", "4.0"]]
        self._test_linked({'telephone': '', 'publish': {'telephone': True}}, vcard)

    def test_fax_publish(self):
        vcard = [["version", {}, "text", "4.0"], ['tel', {'type': ['fax']}, 'uri', 'tel:+1.234']]
        self._test_linked({'fax': '+1.234', 'publish': {'fax': True}}, vcard)

    def test_fax_unpublish(self):
        vcard = [["version", {}, "text", "4.0"]]
        self._test_linked({'fax': '+1.234', 'publish': {'fax': False}}, vcard)

    def test_fax_empty(self):
        vcard = [["version", {}, "text", "4.0"]]
        self._test_linked({'fax': '', 'publish': {'fax': True}}, vcard)

    def test_email_publish(self):
        vcard = [["version", {}, "text", "4.0"], ['email', {'type': ''}, 'text', 'kryten@example.org']]
        self._test_linked({'emails': ['kryten@example.org'], 'publish': {'emails': True}}, vcard)

    def test_email_unpublish(self):
        vcard = [["version", {}, "text", "4.0"]]
        self._test_linked({'emails': ['kryten@example.org'], 'publish': {'emails': False}}, vcard)

    def test_email_empty(self):
        vcard = [["version", {}, "text", "4.0"]]
        self._test_linked({'emails': [], 'publish': {'emails': True}}, vcard)

    def test_changed(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'),
            updated=ObjectEvent(registrar_handle='NOVA5', timestamp=datetime(1988, 9, 13, tzinfo=timezone.utc)))
        contact = Contact(contact_id='2X4B', contact_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events)

        events_data = [
            {'eventAction': 'registration', 'eventDate': '1988-09-06T00:00:00+00:00', 'eventActor': 'DIVADROID'},
            {'eventAction': 'last changed', 'eventDate': '1988-09-13T00:00:00+00:00'}]
        data = {
            'vcardArray': ['vcard', [["version", {}, "text", "4.0"]]],
            'events': events_data,
            'status': ['associated'],
        }
        self._test(contact, {ObjectStatus.LINKED: True}, data)

    def test_transfer(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='NOVA5', timestamp=datetime(1988, 9, 13, tzinfo=timezone.utc)))
        contact = Contact(contact_id='2X4B', contact_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events)

        events_data = [
            {'eventAction': 'registration', 'eventDate': '1988-09-06T00:00:00+00:00', 'eventActor': 'DIVADROID'},
            {'eventAction': 'transfer', 'eventDate': '1988-09-13T00:00:00+00:00'}]
        data = {
            'vcardArray': ['vcard', [["version", {}, "text", "4.0"]]],
            'events': events_data,
            'status': ['associated'],
        }
        self._test(contact, {ObjectStatus.LINKED: True}, data)

    def test_unlinked_port43(self):
        contact = Contact(contact_id='2X4B', contact_handle='KRYTEN', sponsoring_registrar='HOLLY')
        data = {'remarks': [{"description": ["Omitting data because contact is not linked to any registry object."]}],
                'port43': 'whois.example.org'}
        with override_settings(RDAP_UNIX_WHOIS='whois.example.org'):
            self._test(contact, {}, data)

    def test_linked_port43(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'))
        contact = Contact(contact_id='2X4B', contact_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events)

        events_data = [
            {'eventAction': 'registration', 'eventDate': '1988-09-06T00:00:00+00:00', 'eventActor': 'DIVADROID'}]
        data = {
            'vcardArray': ['vcard', [["version", {}, "text", "4.0"]]],
            'events': events_data,
            'status': ['associated'],
            'port43': 'whois.example.org',
        }
        with override_settings(RDAP_UNIX_WHOIS='whois.example.org'):
            self._test(contact, {ObjectStatus.LINKED: True}, data)


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
