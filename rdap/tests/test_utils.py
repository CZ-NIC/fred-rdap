# -*- coding: utf-8 -*-
from datetime import datetime

from django.test import SimpleTestCase
from django.test.utils import override_settings
from django.utils import timezone
from mock import Mock

from rdap.rdap_rest import rdap_utils
from rdap.rdap_rest.whois import _INTERFACE


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
        self.assertEqual(rdap_utils.rdap_status_mapping([]), set(['active']))

    def test_unknown_keys(self):
        self.assertEqual(rdap_utils.rdap_status_mapping(['foobar']), set([]))
        self.assertEqual(rdap_utils.rdap_status_mapping(['barbaz']), set([]))
        self.assertEqual(rdap_utils.rdap_status_mapping(['bazfoo']), set([]))
        self.assertEqual(rdap_utils.rdap_status_mapping(['why-do-cows-moo']), set([]))

    def test_defined_mapping(self):
        defined = (
            (['addPeriod'], set([])),
            (['autoRenewPeriod'], set([])),
            (['clientDeleteProhibited'], set([])),
            (['clientHold'], set([])),
            (['clientRenewProhibited'], set([])),
            (['clientTransferProhibited'], set([])),
            (['clientUpdateProhibited'], set([])),
            (['inactive'], set(['inactive'])),
            (['linked'], set(['associated'])),
            (['ok'], set(['active'])),
            (['pendingCreate'], set(['pending create'])),
            (['pendingDelete'], set(['pending delete'])),
            (['pendingRenew'], set(['pending renew'])),
            (['pendingRestore'], set([])),
            (['pendingTransfer'], set(['pending transfer'])),
            (['pendingUpdate'], set(['pending update'])),
            (['redemptionPeriod'], set([])),
            (['renewPeriod'], set([])),
            (['serverDeleteProhibited'], set([])),
            (['serverRenewProhibited'], set([])),
            (['serverTransferProhibited'], set([])),
            (['serverUpdateProhibited'], set([])),
            (['serverHold'], set([])),
            (['transferPeriod'], set([])),
            (['validatedContact'], set(['validated'])),
            (['contactPassedManualVerification'], set(['validated'])),
            (['deleteCandidate'], set(['pending delete'])),
            (['outzone'], set(['inactive'])),
        )
        for in_list, out_set in defined:
            self.assertEqual(rdap_utils.rdap_status_mapping(in_list), out_set)

    def test_combination_4_mapped_1_nomap(self):
        in_list = ['pendingCreate', 'pendingDelete', 'pendingRenew', 'pendingRestore', 'pendingTransfer']
        out_set = set(['pending create', 'pending delete', 'pending renew', 'pending transfer'])
        self.assertEqual(rdap_utils.rdap_status_mapping(in_list), out_set)

    def test_combination_same_mapped_value_just_once(self):
        in_list = ['validatedContact', 'contactPassedManualVerification', 'deleteCandidate']
        out_set = set(['validated', 'pending delete'])
        self.assertEqual(rdap_utils.rdap_status_mapping(in_list), out_set)


class TestInputFqdnProcessing(SimpleTestCase):

    def test_ok_a_input(self):
        self.assertEqual(rdap_utils.preprocess_fqdn(u'skvirukl.example'), 'skvirukl.example')
        self.assertEqual(rdap_utils.preprocess_fqdn('skvirukl.example'), 'skvirukl.example')

    def test_ok_idn_input(self):
        self.assertEqual(rdap_utils.preprocess_fqdn(u'skvírůkl.example'), 'xn--skvrkl-5va55h.example')
        self.assertEqual(rdap_utils.preprocess_fqdn(u'xn--skvrkl-5va55h.example'), 'xn--skvrkl-5va55h.example')

    def test_bad_idn_input(self):
        self.assertRaises(rdap_utils.InvalidIdn, rdap_utils.preprocess_fqdn, u'xn--skvrkl-ňúríkl.example')


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


class TestUnwrapDatetime(SimpleTestCase):

    def test_use_tz_false(self):
        idl_date = _INTERFACE.Date(22, 12, 2001)
        idl_datetime = _INTERFACE.DateTime(idl_date, 23, 2, 30)
        with override_settings(USE_TZ=False, TIME_ZONE='UTC'):
            self.assertEqual(rdap_utils.unwrap_datetime(idl_datetime), datetime(2001, 12, 22, 23, 2, 30))

    def test_use_tz_true(self):
        idl_date = _INTERFACE.Date(22, 12, 2001)
        idl_datetime = _INTERFACE.DateTime(idl_date, 23, 2, 30)
        with override_settings(USE_TZ=True, TIME_ZONE='UTC'):
            self.assertEqual(
                rdap_utils.unwrap_datetime(idl_datetime),
                datetime(2001, 12, 22, 23, 2, 30, tzinfo=timezone.utc)
            )

    def test_junk(self):
        idl_date = _INTERFACE.Date(22, 14, 2001)
        idl_datetime = _INTERFACE.DateTime(idl_date, 23, 2, 30)
        self.assertRaises(ValueError, rdap_utils.unwrap_datetime, idl_datetime)


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
        self.assertEqual(dst_dict, {'unicodeName': u'skvírůkl.example'})

        dst_dict = {'k': 'v'}
        rdap_utils.add_unicode_name(dst_dict, 'xn--skvrkl-5va55h.example')
        self.assertEqual(dst_dict, {'k': 'v', 'unicodeName': u'skvírůkl.example'})

        dst_dict = {'unicodeName': 'please rewrite!'}
        rdap_utils.add_unicode_name(dst_dict, 'xn--skvrkl-5va55h.example')
        self.assertEqual(dst_dict, {'unicodeName': u'skvírůkl.example'})
