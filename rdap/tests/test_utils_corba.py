"""Tests for `rdap.rdap_rest.whois` module."""
from __future__ import unicode_literals

from datetime import datetime

from django.test import SimpleTestCase
from django.utils import timezone
from fred_idl.Registry import IsoDateTime

from rdap.utils.corba import RdapCorbaRecoder


class TestRdapCorbaRecoder(SimpleTestCase):
    """Test `RdapCorbaRecoder` class."""

    def test_decode_isodatetime_aware(self):
        recoder = RdapCorbaRecoder()
        with self.settings(USE_TZ=True):
            self.assertEqual(recoder.decode(IsoDateTime('2001-02-03T12:13:14Z')),
                             datetime(2001, 2, 3, 12, 13, 14, tzinfo=timezone.utc))

    def test_decode_isodatetime_naive(self):
        recoder = RdapCorbaRecoder()
        with self.settings(USE_TZ=False, TIME_ZONE='Europe/Prague'):
            self.assertEqual(recoder.decode(IsoDateTime('2001-02-03T12:13:14Z')),
                             datetime(2001, 2, 3, 13, 13, 14))
