#
# Copyright (C) 2017-2022  CZ.NIC, z. s. p. o.
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

"""
Example django settings for RDAP project.

Do not use on production - DEBUG settings are turned on.
"""
###############################################################################
#                      RDAP Server Configuration File                         #
###############################################################################

# ## Django Settings ##########################################################
#
# Note: Refer to the Django documentation for a description.
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'SecretKey'
DEBUG = True
ALLOWED_HOSTS = ['*']

TIME_ZONE = 'UTC'
USE_TZ = True

INSTALLED_APPS = ('rdap.apps.RdapAppConfig', )

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
)

ROOT_URLCONF = 'rdap.urls'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {'format': '%(asctime)s - %(name)s - %(levelname)-8s - %(message)s'},
    },
    'handlers': {
        'console': {'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'simple'},
    },
    'loggers': {
        '': {'handlers': ['console'],
             'level': 'DEBUG'},
    },
}


# ## RDAP Server Settings #####################################################

# #### WHOIS URLs configuration
# Unix Whois server address
# RDAP_UNIX_WHOIS = None

# Maximum signature lifetime (seconds) used in secureDNS
# RDAP_MAX_SIG_LIFE = None
# The disclaimer notice that is included in each response
# RDAP_DISCLAIMER = None
