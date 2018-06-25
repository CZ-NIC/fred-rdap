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

# #### CORBA configuration
# Naming service address (host[:port])
# RDAP_CORBA_NETLOC = 'localhost'
# Naming service context
# RDAP_CORBA_CONTEXT = 'fred'

# #### WHOIS URLs configuration
# Base of URLs
RDAP_ROOT_URL = ''
# Unix Whois server address
UNIX_WHOIS_HOST = ''

# Maximum signature lifetime (seconds) used in secureDNS
DNS_MAX_SIG_LIFE = 1209600
# File path of the disclaimer notice that is included in each response
DISCLAIMER_FILE = ''
