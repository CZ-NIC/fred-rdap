# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2020  CZ.NIC, z. s. p. o.
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
from datetime import datetime
from unittest.mock import Mock

from django.test import SimpleTestCase
from django.test.utils import override_settings
from django.utils import timezone

from rdap.rdap_rest import rdap_utils


class TestDisclosableOutput(SimpleTestCase):

    def test_show(self):
        dv = Mock()
        dv.disclose = True
        dv.value = 'Arthur Dent'
        self.assertTrue(rdap_utils.disclosable_nonempty(dv))

        dv.value = ''
        self.assertFalse(rdap_utils.disclosable_nonempty(dv))

    def test_hide(self):
        dv = Mock()
        dv.disclose = False
        dv.value = 'Ford Prefect'
        self.assertFalse(rdap_utils.disclosable_nonempty(dv))

        dv.value = ''
        self.assertFalse(rdap_utils.disclosable_nonempty(dv))


class TestStatusMappingDefinition(SimpleTestCase):

    def test_ok_status_special_behaviour(self):
        self.assertEqual(rdap_utils.rdap_status_mapping([]), ['active'])

    def test_unknown_keys(self):
        self.assertEqual(rdap_utils.rdap_status_mapping(['foobar']), [])
        self.assertEqual(rdap_utils.rdap_status_mapping(['barbaz']), [])
        self.assertEqual(rdap_utils.rdap_status_mapping(['bazfoo']), [])
        self.assertEqual(rdap_utils.rdap_status_mapping(['why-do-cows-moo']), [])

    def test_defined_mapping(self):
        defined = (
            (['inactive'], ['inactive']),
            (['linked'], ['associated']),
            (['ok'], ['active']),
            (['outzone'], ['inactive']),
        )
        for in_list, out_set in defined:
            self.assertEqual(rdap_utils.rdap_status_mapping(in_list), out_set)

    def test_combination_4_mapped_1_nomap(self):
        in_list = ['pendingCreate', 'pendingDelete', 'pendingRenew', 'unknown', 'pendingTransfer']
        out_set = ['pending create', 'pending delete', 'pending renew', 'pending transfer']
        self.assertCountEqual(rdap_utils.rdap_status_mapping(in_list), out_set)

    def test_combination_same_mapped_value_just_once(self):
        in_list = ['validatedContact', 'contactPassedManualVerification', 'deleteCandidate']
        out_set = ['validated', 'pending delete']
        self.assertCountEqual(rdap_utils.rdap_status_mapping(in_list), out_set)


class TestInputFqdnProcessing(SimpleTestCase):

    def test_ok_a_input(self):
        self.assertEqual(rdap_utils.preprocess_fqdn('skvirukl.example'), 'skvirukl.example')
        self.assertEqual(rdap_utils.preprocess_fqdn('skvirukl.example'), 'skvirukl.example')

    def test_ok_idn_input(self):
        self.assertEqual(rdap_utils.preprocess_fqdn('skvírůkl.example'), 'xn--skvrkl-5va55h.example')
        self.assertEqual(rdap_utils.preprocess_fqdn('xn--skvrkl-5va55h.example'), 'xn--skvrkl-5va55h.example')

    def test_bad_idn_input(self):
        self.assertRaises(rdap_utils.InvalidIdn, rdap_utils.preprocess_fqdn, 'xn--skvrkl-ňúríkl.example')


class TestRfc3339TimestampFormat(SimpleTestCase):

    def test_utc_dt(self):
        dt = datetime(2015, 5, 9, 10, 31, 51)
        with override_settings(TIME_ZONE='UTC', USE_TZ=False):
            self.assertEqual(rdap_utils.to_rfc3339(dt), '2015-05-09T10:31:51+00:00')

        dt = timezone.make_aware(dt, timezone.utc)
        with override_settings(TIME_ZONE='UTC', USE_TZ=True):
            self.assertEqual(rdap_utils.to_rfc3339(dt), '2015-05-09T10:31:51+00:00')

    def test_strip_ms(self):
        dt = datetime(1986, 4, 26, 1, 23, 58, 12345)
        with override_settings(TIME_ZONE='UTC', USE_TZ=False):
            self.assertEqual(rdap_utils.to_rfc3339(dt), '1986-04-26T01:23:58+00:00')

    def test_non_utc_dt(self):
        dt = datetime(1998, 2, 22, 8, 32, 10)

        with override_settings(TIME_ZONE='Europe/Prague', USE_TZ=False):
            self.assertEqual(rdap_utils.to_rfc3339(dt), '1998-02-22T08:32:10+01:00')

        with override_settings(TIME_ZONE='America/Denver', USE_TZ=True):
            dttz = timezone.make_aware(dt, timezone.get_default_timezone())
            self.assertEqual(rdap_utils.to_rfc3339(dttz), '1998-02-22T08:32:10-07:00')


class TestAddUnicodeName(SimpleTestCase):

    def test_no_add(self):
        dst_dict = {}
        rdap_utils.add_unicode_name(dst_dict, '42.cz')
        self.assertEqual(dst_dict, {})

        dst_dict = {'k': 'v'}
        rdap_utils.add_unicode_name(dst_dict, '42.cz')
        self.assertEqual(dst_dict, {'k': 'v'})

    def test_add(self):
        dst_dict = {}
        rdap_utils.add_unicode_name(dst_dict, 'xn--skvrkl-5va55h.example')
        self.assertEqual(dst_dict, {'unicodeName': 'skvírůkl.example'})

        dst_dict = {'k': 'v'}
        rdap_utils.add_unicode_name(dst_dict, 'xn--skvrkl-5va55h.example')
        self.assertEqual(dst_dict, {'k': 'v', 'unicodeName': 'skvírůkl.example'})

        dst_dict = {'unicodeName': 'please rewrite!'}
        rdap_utils.add_unicode_name(dst_dict, 'xn--skvrkl-5va55h.example')
        self.assertEqual(dst_dict, {'unicodeName': 'skvírůkl.example'})
