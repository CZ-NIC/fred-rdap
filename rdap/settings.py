#
# Copyright (C) 2014-2022  CZ.NIC, z. s. p. o.
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
"""RDAP application settings wrapper."""
import os
from typing import Any, Dict

from appsettings import AppSettings, DictSetting, FileSetting, IntegerSetting, ListSetting, StringSetting
from frgal import make_credentials


class LoggerOptionsSetting(DictSetting):
    """Custom dict setting for logger options."""

    def transform(self, value: Dict[str, Any]) -> Dict[str, Any]:
        """Transform the credentials."""
        value = super().transform(value)
        if 'credentials' in value:
            value['credentials'] = make_credentials(**value['credentials'])
        return value


class RdapAppSettings(AppSettings):
    """RDAP specific settings."""

    CORBA_NETLOC = StringSetting(default='localhost')
    CORBA_CONTEXT = StringSetting(default='fred')
    LOGGER = StringSetting(default='grill.DummyLoggerClient')
    LOGGER_OPTIONS = LoggerOptionsSetting(default={})
    REGISTRY_NETLOC = StringSetting(required=True)
    REGISTRY_SSL_CERT = FileSetting(default=None, mode=os.R_OK)
    DISCLAIMER = ListSetting(default=None)
    UNIX_WHOIS = StringSetting(default=None)
    MAX_SIG_LIFE = IntegerSetting(default=None)

    class Meta:
        setting_prefix = 'RDAP_'


RDAP_SETTINGS = RdapAppSettings()
