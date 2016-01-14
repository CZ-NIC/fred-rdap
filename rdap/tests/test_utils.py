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
        self.assertEqual(rdap_utils.rdap_status_mapping([]), rdap_utils.rdap_status_mapping(['ok']))

    def test_unknown_key(self):
        unknown = 'foobar'
        self.assertTrue(unknown not in rdap_utils.RDAP_STATUS_MAPPING.keys())
        self.assertEqual(rdap_utils.rdap_status_mapping([unknown]), set([]))

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

    def test_combination(self):
        defined = (
            (
                ['pendingCreate', 'pendingDelete', 'pendingRenew', 'pendingRestore', 'pendingTransfer'],
                set(['pending create', 'pending delete', 'pending renew', 'pending transfer'])
            ),
            (
                ['validatedContact', 'contactPassedManualVerification', 'deleteCandidate'],
                set(['validated', 'pending delete'])
            ),
        )
        for in_list, out_set in defined:
            self.assertEqual(rdap_utils.rdap_status_mapping(in_list), out_set)
