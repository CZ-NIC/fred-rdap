"""AppConfig definition."""
from __future__ import unicode_literals

from django.apps import AppConfig

from .settings import RDAP_SETTINGS


class RdapAppConfig(AppConfig):
    """RDAP specific app config."""

    name = 'rdap'

    def ready(self):
        RDAP_SETTINGS.check()
