#
# Copyright (C) 2014-2018  CZ.NIC, z. s. p. o.
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

"""RDAP application settings wrapper."""
from __future__ import unicode_literals

from appsettings import AppSettings, ListSetting, StringSetting


class RdapAppSettings(AppSettings):
    """RDAP specific settings."""

    CORBA_NETLOC = StringSetting(default='localhost')
    CORBA_CONTEXT = StringSetting(default='fred')
    DISCLAIMER = ListSetting(default=None)
    UNIX_WHOIS = StringSetting(default=None)

    class Meta:
        setting_prefix = 'RDAP_'


RDAP_SETTINGS = RdapAppSettings()
