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
