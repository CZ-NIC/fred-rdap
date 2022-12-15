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
from datetime import datetime, timezone
from ipaddress import IPv4Address, IPv6Address
from typing import Any, Dict, List, Optional
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase, override_settings
from regal import Address, Contact, DnsHost, DnsKey, Domain, Keyset, Nsset, ObjectEvent, ObjectEvents

from rdap.constants import ObjectStatus
from rdap.rdap_rest.domain import domain_to_dict
from rdap.rdap_rest.entity import contact_to_dict
from rdap.rdap_rest.keyset import keyset_to_dict
from rdap.rdap_rest.nameserver import nameserver_to_dict
from rdap.rdap_rest.nsset import nsset_to_dict
from rdap.rdap_rest.rdap_utils import ObjectClassName


@override_settings(ALLOWED_HOSTS=['rdap.example'], RDAP_UNIX_WHOIS=None)
class TestDomainToDict(SimpleTestCase):
    """Test `rdap.rdap_rest.domain.domain_to_dict` function."""

    def setUp(self):
        self.request = RequestFactory(HTTP_HOST='rdap.example').get('/dummy/')

        patcher = patch('rdap.rdap_rest.domain.CONTACT_CLIENT', spec=('get_contact_info', ))
        self.addCleanup(patcher.stop)
        self.contact_mock = patcher.start()
        self.contact_mock.get_contact_info.return_value = Contact(contact_id='2X4B', contact_handle='KRYTEN')
        patcher = patch('rdap.rdap_rest.domain.DOMAIN_CLIENT', spec=('get_domain_state', ))
        self.addCleanup(patcher.stop)
        self.domain_mock = patcher.start()
        patcher = patch('rdap.rdap_rest.domain.KEYSET_CLIENT', spec=('get_keyset_info', ))
        self.addCleanup(patcher.stop)
        self.keyset_mock = patcher.start()
        patcher = patch('rdap.rdap_rest.domain.NSSET_CLIENT', spec=('get_nsset_info', ))
        self.addCleanup(patcher.stop)
        self.nsset_mock = patcher.start()

    def _test(self, domain: Domain, states: Dict[str, bool], data: Dict[str, Any]) -> None:
        self.domain_mock.get_domain_state.return_value = states

        result = domain_to_dict(domain, self.request)

        link = {'value': 'http://rdap.example/domain/example.org', 'rel': 'self',
                'href': 'http://rdap.example/domain/example.org', 'type': 'application/rdap+json'}
        defaults = {
            'rdapConformance': ["rdap_level_0", 'fred_version_0'],
            'objectClassName': ObjectClassName.DOMAIN,
            'handle': 'example.org',
            'ldhName': 'example.org',
            'links': [link],
        }
        self.assertEqual(result, dict(defaults, **data))

    def test_delete_candidate(self):
        domain = Domain(domain_id='EXAMPLE', fqdn='example.org', sponsoring_registrar='HOLLY')
        data = {'status': ['pending delete']}
        self._test(domain, {'deleteCandidate': True}, data)

    def _test_simple(self, domain_kwargs: Dict[str, Any], extra_data: Dict[str, Any],
                     *, states: Optional[Dict[str, bool]] = None) -> None:
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'))
        kwargs = dict(
            {'domain_id': 'EXAMPLE', 'fqdn': 'example.org', 'sponsoring_registrar': 'HOLLY', 'events': events,
             'registrant': '2X4B', 'expires_at': datetime(1999, 4, 5, tzinfo=timezone.utc)},
            **domain_kwargs)
        domain = Domain(**kwargs)
        events_data = [
            {'eventAction': 'registration', 'eventDate': '1988-09-06T00:00:00+00:00'},
            {'eventAction': 'expiration', 'eventDate': '1999-04-05T00:00:00+00:00'}]
        link = {'value': 'http://rdap.example/entity/KRYTEN', 'rel': 'self',
                'href': 'http://rdap.example/entity/KRYTEN', 'type': 'application/rdap+json'}
        entities = [
            {'objectClassName': ObjectClassName.ENTITY, 'handle': 'KRYTEN', 'roles': ['registrant'], 'links': [link]},
            {'objectClassName': ObjectClassName.ENTITY, 'handle': 'HOLLY', 'roles': ['registrar']}]
        data = {'events': events_data, 'entities': entities, 'status': ['active']}
        data.update(**extra_data)
        self._test(domain, states or {}, data)

    def test_simple(self):
        self._test_simple({}, {})

    def test_port43(self):
        with override_settings(RDAP_UNIX_WHOIS='whois.example.org'):
            self._test_simple({}, {'port43': 'whois.example.org'})

    def test_admin_contacts(self):
        self.contact_mock.get_contact_info.side_effect = [Contact(contact_id='2X4B', contact_handle='KRYTEN'),
                                                          Contact(contact_id='ID-RIMMER', contact_handle='RIMMER')]
        link = {'value': 'http://rdap.example/entity/KRYTEN', 'rel': 'self',
                'href': 'http://rdap.example/entity/KRYTEN', 'type': 'application/rdap+json'}
        admin = {'value': 'http://rdap.example/entity/RIMMER', 'rel': 'self',
                 'href': 'http://rdap.example/entity/RIMMER', 'type': 'application/rdap+json'}
        entities = [
            {'objectClassName': ObjectClassName.ENTITY, 'handle': 'KRYTEN', 'roles': ['registrant'], 'links': [link]},
            {'objectClassName': ObjectClassName.ENTITY, 'handle': 'HOLLY', 'roles': ['registrar']},
            {'objectClassName': ObjectClassName.ENTITY, 'handle': 'RIMMER', 'roles': ['administrative'],
             'links': [admin]}]
        self._test_simple({'administrative_contacts': ['ID-RIMMER']}, {'entities': entities})

    def test_statuses(self):
        data = {'status': ['associated']}
        self._test_simple({}, data, states={ObjectStatus.LINKED: True})

    def test_changed(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='QUEEG-500'),
            updated=ObjectEvent(registrar_handle='NOVA5', timestamp=datetime(1988, 9, 13, tzinfo=timezone.utc)))
        events_data = [
            {'eventAction': 'registration', 'eventDate': '1988-09-06T00:00:00+00:00'},
            {'eventAction': 'expiration', 'eventDate': '1999-04-05T00:00:00+00:00'},
            {'eventAction': 'last changed', 'eventDate': '1988-09-13T00:00:00+00:00'}]
        data = {
            'events': events_data,
        }
        self._test_simple({'events': events}, data)

    def test_transfer(self):
        events = ObjectEvents(
            registered=ObjectEvent(registrar_handle='DIVADROID', timestamp=datetime(1988, 9, 6, tzinfo=timezone.utc)),
            transferred=ObjectEvent(registrar_handle='NOVA5', timestamp=datetime(1988, 9, 13, tzinfo=timezone.utc)))
        events_data = [
            {'eventAction': 'registration', 'eventDate': '1988-09-06T00:00:00+00:00'},
            {'eventAction': 'expiration', 'eventDate': '1999-04-05T00:00:00+00:00'},
            {'eventAction': 'transfer', 'eventDate': '1988-09-13T00:00:00+00:00'}]
        data = {
            'events': events_data,
        }
        self._test_simple({'events': events}, data)

    def test_validation_expires(self):
        events_data = [
            {'eventAction': 'registration', 'eventDate': '1988-09-06T00:00:00+00:00'},
            {'eventAction': 'expiration', 'eventDate': '1999-04-05T00:00:00+00:00'},
            {'eventAction': 'enum validation expiration', 'eventDate': '1988-09-13T00:00:00+00:00'}]
        data = {
            'events': events_data,
        }
        self._test_simple({'validation_expires_at': datetime(1988, 9, 13, tzinfo=timezone.utc)}, data)

    def test_nsset_empty(self):
        nsset = Nsset(nsset_id='ID-EXAMPLE', nsset_handle='EXAMPLE')
        self.nsset_mock.get_nsset_info.return_value = nsset
        nsset_link = 'http://rdap.example/fred_nsset/EXAMPLE'
        nsset_data = {
            "objectClassName": ObjectClassName.NSSET, 'handle': 'EXAMPLE', 'nameservers': [],
            'links': [{'value': nsset_link, 'rel': 'self', 'href': nsset_link, 'type': 'application/rdap+json'}]}
        self._test_simple({'nsset': 'ID-EXAMPLE'}, {'nameservers': [], 'fred_nsset': nsset_data})

    def test_nsset_empty_host(self):
        nsset = Nsset(nsset_id='ID-EXAMPLE', nsset_handle='EXAMPLE',
                      dns_hosts=[DnsHost(fqdn='ns.example.org', ip_addresses=[])])
        self.nsset_mock.get_nsset_info.return_value = nsset
        link = 'http://rdap.example/nameserver/ns.example.org'
        ns = {"objectClassName": ObjectClassName.NAMESERVER, 'handle': 'ns.example.org', 'ldhName': 'ns.example.org',
              'links': [{'value': link, 'rel': 'self', 'href': link, 'type': 'application/rdap+json'}]}
        nsset_link = 'http://rdap.example/fred_nsset/EXAMPLE'
        nsset_data = {
            "objectClassName": ObjectClassName.NSSET, 'handle': 'EXAMPLE', 'nameservers': [ns],
            'links': [{'value': nsset_link, 'rel': 'self', 'href': nsset_link, 'type': 'application/rdap+json'}]}
        self._test_simple({'nsset': 'ID-EXAMPLE'}, {'nameservers': [ns], 'fred_nsset': nsset_data})

    def test_nameserver_ipv4(self):
        nsset = Nsset(nsset_id='ID-EXAMPLE', nsset_handle='EXAMPLE',
                      dns_hosts=[DnsHost(fqdn='ns.example.org', ip_addresses=[IPv4Address('127.0.0.1')])])
        self.nsset_mock.get_nsset_info.return_value = nsset
        link = 'http://rdap.example/nameserver/ns.example.org'
        ns = {"objectClassName": ObjectClassName.NAMESERVER, 'handle': 'ns.example.org', 'ldhName': 'ns.example.org',
              'links': [{'value': link, 'rel': 'self', 'href': link, 'type': 'application/rdap+json'}],
              'ipAddresses': {'v4': ['127.0.0.1']}}
        nsset_link = 'http://rdap.example/fred_nsset/EXAMPLE'
        nsset_data = {
            "objectClassName": ObjectClassName.NSSET, 'handle': 'EXAMPLE', 'nameservers': [ns],
            'links': [{'value': nsset_link, 'rel': 'self', 'href': nsset_link, 'type': 'application/rdap+json'}]}
        self._test_simple({'nsset': 'ID-EXAMPLE'}, {'nameservers': [ns], 'fred_nsset': nsset_data})

    def test_nameserver_ipv6(self):
        nsset = Nsset(nsset_id='ID-EXAMPLE', nsset_handle='EXAMPLE',
                      dns_hosts=[DnsHost(fqdn='ns.example.org', ip_addresses=[IPv6Address('::1')])])
        self.nsset_mock.get_nsset_info.return_value = nsset
        link = 'http://rdap.example/nameserver/ns.example.org'
        ns = {"objectClassName": ObjectClassName.NAMESERVER, 'handle': 'ns.example.org', 'ldhName': 'ns.example.org',
              'links': [{'value': link, 'rel': 'self', 'href': link, 'type': 'application/rdap+json'}],
              'ipAddresses': {'v6': ['::1']}}
        nsset_link = 'http://rdap.example/fred_nsset/EXAMPLE'
        nsset_data = {
            "objectClassName": ObjectClassName.NSSET, 'handle': 'EXAMPLE', 'nameservers': [ns],
            'links': [{'value': nsset_link, 'rel': 'self', 'href': nsset_link, 'type': 'application/rdap+json'}]}
        self._test_simple({'nsset': 'ID-EXAMPLE'}, {'nameservers': [ns], 'fred_nsset': nsset_data})

    def test_keyset_empty(self):
        keyset = Keyset(keyset_id='ID-EXAMPLE', keyset_handle='EXAMPLE')
        self.keyset_mock.get_keyset_info.return_value = keyset
        keyset_link = 'http://rdap.example/fred_keyset/EXAMPLE'
        keyset_data = {
            "objectClassName": ObjectClassName.KEYSET, 'handle': 'EXAMPLE', 'dns_keys': [],
            'links': [{'value': keyset_link, 'rel': 'self', 'href': keyset_link, 'type': 'application/rdap+json'}]}
        data = {'secureDNS': {'zoneSigned': True, 'delegationSigned': True, 'keyData': []},
                'fred_keyset': keyset_data}
        self._test_simple({'keyset': 'ID-EXAMPLE'}, data)

    def test_keyset_max_sig_life(self):
        keyset = Keyset(keyset_id='ID-EXAMPLE', keyset_handle='EXAMPLE')
        self.keyset_mock.get_keyset_info.return_value = keyset
        keyset_link = 'http://rdap.example/fred_keyset/EXAMPLE'
        keyset_data = {
            "objectClassName": ObjectClassName.KEYSET, 'handle': 'EXAMPLE', 'dns_keys': [],
            'links': [{'value': keyset_link, 'rel': 'self', 'href': keyset_link, 'type': 'application/rdap+json'}]}
        data = {'secureDNS': {'zoneSigned': True, 'delegationSigned': True, 'keyData': [], 'maxSigLife': 42},
                'fred_keyset': keyset_data}
        with override_settings(RDAP_MAX_SIG_LIFE=42):
            self._test_simple({'keyset': 'ID-EXAMPLE'}, data)

    def test_keyset_dnskey(self):
        keyset = Keyset(keyset_id='ID-EXAMPLE', keyset_handle='EXAMPLE',
                        dns_keys=[DnsKey(flags=42, protocol=3, alg=-15, key='Gazpacho!')])
        self.keyset_mock.get_keyset_info.return_value = keyset
        key = {'flags': 42, 'protocol': 3, 'algorithm': -15, 'publicKey': 'Gazpacho!'}
        keyset_link = 'http://rdap.example/fred_keyset/EXAMPLE'
        keyset_data = {
            "objectClassName": ObjectClassName.KEYSET, 'handle': 'EXAMPLE', 'dns_keys': [key],
            'links': [{'value': keyset_link, 'rel': 'self', 'href': keyset_link, 'type': 'application/rdap+json'}]}
        data = {'secureDNS': {'zoneSigned': True, 'delegationSigned': True, 'keyData': [key]},
                'fred_keyset': keyset_data}
        self._test_simple({'keyset': 'ID-EXAMPLE'}, data)


@override_settings(ALLOWED_HOSTS=['rdap.example'], RDAP_UNIX_WHOIS=None)
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

        patcher = patch('rdap.rdap_rest.nsset.NSSET_CLIENT', spec=('get_nsset_state', ))
        self.addCleanup(patcher.stop)
        self.nsset_mock = patcher.start()

    def test_simple(self):
        result = nameserver_to_dict('ns.example.org', self.request)

        link = {'value': 'http://rdap.example/nameserver/ns.example.org', 'rel': 'self',
                'href': 'http://rdap.example/nameserver/ns.example.org', 'type': 'application/rdap+json'}
        data = {
            'rdapConformance': ["rdap_level_0"],
            'objectClassName': ObjectClassName.NAMESERVER,
            'handle': 'ns.example.org',
            'ldhName': 'ns.example.org',
            'links': [link],
        }
        self.assertEqual(result, data)


@override_settings(ALLOWED_HOSTS=['rdap.example'], RDAP_UNIX_WHOIS=None)
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
