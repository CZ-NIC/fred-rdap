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
from ipaddress import IPv4Address, IPv6Address
from typing import Any, Dict, List
from unittest.mock import patch, sentinel

from django.test import RequestFactory, SimpleTestCase, override_settings
from fred_idl.Registry.Whois import Domain, KeySet, NameServer, NSSet
from regal import Address, Contact, DnsHost, DnsKey, Keyset, Nsset, ObjectEvent, ObjectEvents

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


@override_settings(ALLOWED_HOSTS=['rdap.example'], RDAP_UNIX_WHOIS=None, USE_TZ=True)
class TestKeysetToDict(SimpleTestCase):
    """Test `rdap.rdap_rest.domain.keyset_to_dict` function."""

    def setUp(self):
        self.request = RequestFactory(HTTP_HOST='rdap.example').get('/dummy/')

        patcher = patch('rdap.rdap_rest.keyset.KEYSET_CLIENT', spec=('get_keyset_state', ))
        self.addCleanup(patcher.stop)
        self.keyset_mock = patcher.start()
        patcher = patch('rdap.rdap_rest.keyset.CONTACT_CLIENT', spec=('get_contact_info', ))
        self.addCleanup(patcher.stop)
        self.contact_mock = patcher.start()

    def _test(self, keyset: Keyset, states: Dict[str, bool], data: Dict[str, Any]) -> None:
        self.keyset_mock.get_keyset_state.return_value = states

        result = keyset_to_dict(keyset, self.request)

        link = {'value': 'http://rdap.example/fred_keyset/KRYTEN', 'rel': 'self',
                'href': 'http://rdap.example/fred_keyset/KRYTEN', 'type': 'application/rdap+json'}
        events_data = [{'eventAction': 'registration', 'eventDate': '1988-09-06T00:00:00+00:00'}]
        defaults = {
            'rdapConformance': ["rdap_level_0", "fred_version_0"],
            'objectClassName': ObjectClassName.KEYSET,
            'handle': 'KRYTEN',
            'links': [link],
            'entities': [{'objectClassName': ObjectClassName.ENTITY, 'handle': 'HOLLY', 'roles': ['registrar']}],
            'events': events_data,
            'status': ['active'],
        }
        self.assertEqual(result, dict(defaults, **data))

    def test_simple(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'))
        keyset = Keyset(keyset_id='2X4B', keyset_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events)
        self._test(keyset, {}, {})

    def test_port43(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'))
        keyset = Keyset(keyset_id='2X4B', keyset_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events)
        data = {'port43': 'whois.example.org'}
        with override_settings(RDAP_UNIX_WHOIS='whois.example.org'):
            self._test(keyset, {}, data)

    def test_statuses(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'))
        keyset = Keyset(keyset_id='2X4B', keyset_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events)
        data = {'status': ['associated']}
        self._test(keyset, {ObjectStatus.LINKED: True}, data)

    def test_tech_contacts(self):
        self.contact_mock.get_contact_info.return_value = Contact(contact_id='ID-RIMMER', contact_handle='RIMMER')
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'))
        keyset = Keyset(keyset_id='2X4B', keyset_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events,
                        technical_contacts=['ID-RIMMER'])
        entities = [{'objectClassName': ObjectClassName.ENTITY, 'handle': 'HOLLY', 'roles': ['registrar']}]
        link = 'http://rdap.example/entity/RIMMER'
        entities.append({
            'objectClassName': ObjectClassName.ENTITY,
            'handle': 'RIMMER',
            'roles': ['technical'],
            'links': [{'value': link, 'rel': 'self', 'href': link, 'type': 'application/rdap+json'}],
        })
        self._test(keyset, {}, {'entities': entities})

    def test_dnskey(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'))
        keyset = Keyset(keyset_id='2X4B', keyset_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events,
                        dns_keys=[DnsKey(flags=42, protocol=3, alg=-15, key='Gazpacho!')])
        key = {'flags': 42, 'protocol': 3, 'algorithm': -15, 'publicKey': 'Gazpacho!'}
        self._test(keyset, {}, {'dns_keys': [key]})

    def test_changed(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'),
            updated=ObjectEvent(registrar_handle='NOVA5', timestamp=datetime(1988, 9, 13, tzinfo=timezone.utc)))
        keyset = Keyset(keyset_id='2X4B', keyset_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events)

        events_data = [
            {'eventAction': 'registration', 'eventDate': '1988-09-06T00:00:00+00:00'},
            {'eventAction': 'last changed', 'eventDate': '1988-09-13T00:00:00+00:00'}]
        data = {
            'events': events_data,
        }
        self._test(keyset, {}, data)

    def test_transfer(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='NOVA5', timestamp=datetime(1988, 9, 13, tzinfo=timezone.utc)))
        keyset = Keyset(keyset_id='2X4B', keyset_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events)

        events_data = [
            {'eventAction': 'registration', 'eventDate': '1988-09-06T00:00:00+00:00'},
            {'eventAction': 'transfer', 'eventDate': '1988-09-13T00:00:00+00:00'}]
        data = {
            'events': events_data,
        }
        self._test(keyset, {}, data)


@override_settings(ALLOWED_HOSTS=['rdap.example'])
class TestNameserverToDict(SimpleTestCase):
    """Test `rdap.rdap_rest.domain.nameserver_to_dict` function."""

    def setUp(self):
        self.request = RequestFactory(HTTP_HOST='rdap.example').get('/dummy/')

    def test_simple(self):
        nameserver = NameServer(fqdn='nameserver.example.cz', ip_addresses=[])
        result = nameserver_to_dict(self.request, nameserver)
        self.assertEqual(result['links'][0]['value'], 'http://rdap.example/nameserver/nameserver.example.cz')


@override_settings(ALLOWED_HOSTS=['rdap.example'], RDAP_UNIX_WHOIS=None, USE_TZ=True)
class TestNssetToDict(SimpleTestCase):
    """Test `rdap.rdap_rest.domain.nsset_to_dict` function."""

    def setUp(self):
        self.request = RequestFactory(HTTP_HOST='rdap.example').get('/dummy/')

        patcher = patch('rdap.rdap_rest.nsset.NSSET_CLIENT', spec=('get_nsset_state', ))
        self.addCleanup(patcher.stop)
        self.nsset_mock = patcher.start()
        patcher = patch('rdap.rdap_rest.nsset.CONTACT_CLIENT', spec=('get_contact_info', ))
        self.addCleanup(patcher.stop)
        self.contact_mock = patcher.start()

    def _test(self, nsset: Nsset, states: Dict[str, bool], data: Dict[str, Any]) -> None:
        self.nsset_mock.get_nsset_state.return_value = states

        result = nsset_to_dict(nsset, self.request)

        link = {'value': 'http://rdap.example/fred_nsset/KRYTEN', 'rel': 'self',
                'href': 'http://rdap.example/fred_nsset/KRYTEN', 'type': 'application/rdap+json'}
        events_data = [{'eventAction': 'registration', 'eventDate': '1988-09-06T00:00:00+00:00'}]
        defaults = {
            'rdapConformance': ["rdap_level_0", "fred_version_0"],
            'objectClassName': ObjectClassName.NSSET,
            'handle': 'KRYTEN',
            'links': [link],
            'entities': [{'objectClassName': ObjectClassName.ENTITY, 'handle': 'HOLLY', 'roles': ['registrar']}],
            'events': events_data,
            'nameservers': [],
            'status': ['active'],
        }
        self.assertEqual(result, dict(defaults, **data))

    def test_simple(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'))
        nsset = Nsset(nsset_id='2X4B', nsset_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events)
        self._test(nsset, {}, {})

    def test_port43(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'))
        nsset = Nsset(nsset_id='2X4B', nsset_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events)
        data = {'port43': 'whois.example.org'}
        with override_settings(RDAP_UNIX_WHOIS='whois.example.org'):
            self._test(nsset, {}, data)

    def test_statuses(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'))
        nsset = Nsset(nsset_id='2X4B', nsset_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events)
        data = {'status': ['associated']}
        self._test(nsset, {ObjectStatus.LINKED: True}, data)

    def test_tech_contacts(self):
        self.contact_mock.get_contact_info.return_value = Contact(contact_id='ID-RIMMER', contact_handle='RIMMER')
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'))
        nsset = Nsset(nsset_id='2X4B', nsset_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events,
                      technical_contacts=['ID-RIMMER'])
        entities = [{'objectClassName': ObjectClassName.ENTITY, 'handle': 'HOLLY', 'roles': ['registrar']}]
        link = 'http://rdap.example/entity/RIMMER'
        entities.append({
            'objectClassName': ObjectClassName.ENTITY,
            'handle': 'RIMMER',
            'roles': ['technical'],
            'links': [{'value': link, 'rel': 'self', 'href': link, 'type': 'application/rdap+json'}],
        })
        self._test(nsset, {}, {'entities': entities})

    def test_nameserver_empty(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'))
        nsset = Nsset(nsset_id='2X4B', nsset_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events,
                      dns_hosts=[DnsHost(fqdn='ns.example.org', ip_addresses=[])])
        link = 'http://rdap.example/nameserver/ns.example.org'
        ns = {"objectClassName": ObjectClassName.NAMESERVER, 'handle': 'ns.example.org', 'ldhName': 'ns.example.org',
              'links': [{'value': link, 'rel': 'self', 'href': link, 'type': 'application/rdap+json'}]}
        self._test(nsset, {}, {'nameservers': [ns]})

    def test_nameserver_ipv4(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'))
        nsset = Nsset(nsset_id='2X4B', nsset_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events,
                      dns_hosts=[DnsHost(fqdn='ns.example.org', ip_addresses=[IPv4Address('127.0.0.1')])])
        link = 'http://rdap.example/nameserver/ns.example.org'
        ns = {"objectClassName": ObjectClassName.NAMESERVER, 'handle': 'ns.example.org', 'ldhName': 'ns.example.org',
              'links': [{'value': link, 'rel': 'self', 'href': link, 'type': 'application/rdap+json'}],
              'ipAddresses': {'v4': ['127.0.0.1']}}
        self._test(nsset, {}, {'nameservers': [ns]})

    def test_nameserver_ipv6(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'))
        nsset = Nsset(nsset_id='2X4B', nsset_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events,
                      dns_hosts=[DnsHost(fqdn='ns.example.org', ip_addresses=[IPv6Address('::1')])])
        link = 'http://rdap.example/nameserver/ns.example.org'
        ns = {"objectClassName": ObjectClassName.NAMESERVER, 'handle': 'ns.example.org', 'ldhName': 'ns.example.org',
              'links': [{'value': link, 'rel': 'self', 'href': link, 'type': 'application/rdap+json'}],
              'ipAddresses': {'v6': ['::1']}}
        self._test(nsset, {}, {'nameservers': [ns]})

    def test_changed(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'),
            updated=ObjectEvent(registrar_handle='NOVA5', timestamp=datetime(1988, 9, 13, tzinfo=timezone.utc)))
        nsset = Nsset(nsset_id='2X4B', nsset_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events)

        events_data = [
            {'eventAction': 'registration', 'eventDate': '1988-09-06T00:00:00+00:00'},
            {'eventAction': 'last changed', 'eventDate': '1988-09-13T00:00:00+00:00'}]
        data = {
            'events': events_data,
        }
        self._test(nsset, {}, data)

    def test_transfer(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='NOVA5', timestamp=datetime(1988, 9, 13, tzinfo=timezone.utc)))
        nsset = Nsset(nsset_id='2X4B', nsset_handle='KRYTEN', sponsoring_registrar='HOLLY', events=events)

        events_data = [
            {'eventAction': 'registration', 'eventDate': '1988-09-06T00:00:00+00:00'},
            {'eventAction': 'transfer', 'eventDate': '1988-09-13T00:00:00+00:00'}]
        data = {
            'events': events_data,
        }
        self._test(nsset, {}, data)
