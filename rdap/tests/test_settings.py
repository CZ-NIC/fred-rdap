#
# Copyright (C) 2021  CZ.NIC, z. s. p. o.
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
#
from unittest.mock import call, patch, sentinel

from django.test import SimpleTestCase

from rdap.settings import LoggerOptionsSetting


class LoggerOptionsSettingTest(SimpleTestCase):
    def test_transform_empty(self):
        setting = LoggerOptionsSetting()
        self.assertEqual(setting.transform({}), {})

    def test_transform(self):
        setting = LoggerOptionsSetting()
        self.assertEqual(setting.transform({'netloc': sentinel.netloc}), {'netloc': sentinel.netloc})

    def test_transform_credentials(self):
        setting = LoggerOptionsSetting()
        with patch('rdap.settings.make_credentials', autospec=True, return_value=sentinel.result) as cred_mock:
            self.assertEqual(setting.transform({'credentials': {'ssl_cert': sentinel.cert}}),
                             {'credentials': sentinel.result})
        self.assertEqual(cred_mock.mock_calls, [call(ssl_cert=sentinel.cert)])
