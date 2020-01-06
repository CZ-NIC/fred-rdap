#
# Copyright (C) 2017-2020  CZ.NIC, z. s. p. o.
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

"""Tests for `rdap.rdap_rest.whois` module."""
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
