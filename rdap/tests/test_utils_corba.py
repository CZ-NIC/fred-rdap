"""Tests for `rdap.rdap_rest.whois` module."""
from datetime import date, datetime

from django.test import SimpleTestCase, override_settings
from django.utils import timezone

from rdap.utils.corba import REGISTRY_MODULE, RdapCorbaRecoder


class TestRdapCorbaRecoder(SimpleTestCase):
    """Test `RdapCorbaRecoder` class."""

    def test_decode_date(self):
        recoder = RdapCorbaRecoder()
        self.assertEqual(recoder.decode(REGISTRY_MODULE.Date(1, 3, 2001)), date(2001, 3, 1))

    def test_decode_invalid_date(self):
        recoder = RdapCorbaRecoder()
        self.assertRaises(ValueError, recoder.decode, REGISTRY_MODULE.Date(1, 13, 2001))

    @override_settings(USE_TZ=False, TIME_ZONE='Europe/Prague')
    def test_decode_datetime_naive(self):
        recoder = RdapCorbaRecoder()
        value = REGISTRY_MODULE.DateTime(REGISTRY_MODULE.Date(1, 3, 2001), 12, 1, 26)
        self.assertEqual(recoder.decode(value), datetime(2001, 3, 1, 13, 1, 26))

    @override_settings(USE_TZ=True)
    def test_decode_datetime_aware(self):
        recoder = RdapCorbaRecoder()
        value = REGISTRY_MODULE.DateTime(REGISTRY_MODULE.Date(1, 3, 2001), 12, 1, 26)
        self.assertEqual(recoder.decode(value), datetime(2001, 3, 1, 12, 1, 26, tzinfo=timezone.utc))

    def test_decode_invalid_datetime(self):
        recoder = RdapCorbaRecoder()
        value = REGISTRY_MODULE.DateTime(REGISTRY_MODULE.Date(1, 3, 2001), 12, 1, 89)
        self.assertRaises(ValueError, recoder.decode, value)
