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
