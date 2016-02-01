# -*- coding: utf-8 -*-
from django.test import SimpleTestCase
from mock import Mock

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
