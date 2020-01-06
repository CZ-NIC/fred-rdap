#
# Copyright (C) 2019-2020  CZ.NIC, z. s. p. o.
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
from unittest.mock import call, patch

from django.test import RequestFactory, SimpleTestCase
from fred_idl.Registry.Whois import OBJECT_DELETE_CANDIDATE

from rdap.rdap_rest.whois import get_domain_by_handle
from rdap.utils.corba import WHOIS


class TestGetDomainByHandle(SimpleTestCase):
    def setUp(self):
        patcher = patch.object(WHOIS, 'client', spec=('get_domain_by_handle', ))
        self.addCleanup(patcher.stop)
        patcher.start()

    def test_domain_delete_candidate(self):
        WHOIS.get_domain_by_handle.side_effect = OBJECT_DELETE_CANDIDATE
        request = RequestFactory().get('/dummy/')

        response = get_domain_by_handle(request, 'test.example')

        self.assertEqual(response['handle'], 'test.example')
        self.assertEqual(response['objectClassName'], 'domain')
        self.assertEqual(response['status'], ['pending delete'])

        # Check corba calls
        calls = [call.get_domain_by_handle('test.example')]
        self.assertEqual(WHOIS.client.mock_calls, calls)
