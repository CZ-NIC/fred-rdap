"""Tests for `rdap.rdap_rest.whois` module."""
from datetime import date, datetime

from django.test import SimpleTestCase, override_settings
from django.utils import timezone
from fred_idl.ccReg import DateTimeType, DateType
from fred_idl.Registry import Date, DateTime

from rdap.utils.corba import RdapCorbaRecoder


class TestRdapCorbaRecoder(SimpleTestCase):
    """Test `RdapCorbaRecoder` class."""

    def test_decode_date(self):
        recoder = RdapCorbaRecoder()
        self.assertEqual(recoder.decode(DateType(1, 3, 2001)), date(2001, 3, 1))

    def test_decode_invalid_date(self):
        recoder = RdapCorbaRecoder()
        self.assertRaises(ValueError, recoder.decode, DateType(1, 13, 2001))

    @override_settings(USE_TZ=False, TIME_ZONE='Europe/Prague')
    def test_decode_datetime_naive(self):
        recoder = RdapCorbaRecoder()
        value = DateTimeType(DateType(1, 3, 2001), 12, 1, 26)
        self.assertEqual(recoder.decode(value), datetime(2001, 3, 1, 13, 1, 26))

    @override_settings(USE_TZ=True)
    def test_decode_datetime_aware(self):
        recoder = RdapCorbaRecoder()
        value = DateTimeType(DateType(1, 3, 2001), 12, 1, 26)
        self.assertEqual(recoder.decode(value), datetime(2001, 3, 1, 12, 1, 26, tzinfo=timezone.utc))

    def test_decode_invalid_datetime(self):
        recoder = RdapCorbaRecoder()
        value = DateTimeType(DateType(1, 3, 2001), 12, 1, 89)
        self.assertRaises(ValueError, recoder.decode, value)

    def test_decode_date_registry(self):
        recoder = RdapCorbaRecoder()
        self.assertEqual(recoder.decode(Date(1, 3, 2001)), date(2001, 3, 1))

    def test_decode_invalid_date_registry(self):
        recoder = RdapCorbaRecoder()
        self.assertRaises(ValueError, recoder.decode, Date(1, 13, 2001))

    @override_settings(USE_TZ=False, TIME_ZONE='Europe/Prague')
    def test_decode_datetime_naive_registry(self):
        recoder = RdapCorbaRecoder()
        value = DateTime(Date(1, 3, 2001), 12, 1, 26)
        self.assertEqual(recoder.decode(value), datetime(2001, 3, 1, 13, 1, 26))

    @override_settings(USE_TZ=True)
    def test_decode_datetime_aware_registry(self):
        recoder = RdapCorbaRecoder()
        value = DateTime(Date(1, 3, 2001), 12, 1, 26)
        self.assertEqual(recoder.decode(value), datetime(2001, 3, 1, 12, 1, 26, tzinfo=timezone.utc))

    def test_decode_invalid_datetime_registry(self):
        recoder = RdapCorbaRecoder()
        value = DateTime(Date(1, 3, 2001), 12, 1, 89)
        self.assertRaises(ValueError, recoder.decode, value)
