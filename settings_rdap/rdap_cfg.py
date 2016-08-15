"""
Django settings for rdap project.
"""
###############################################################################
#                      RDAP Server Configuration File                         #
###############################################################################

## Django and Django REST Settings ############################################
#
# Note: Refer to Django and Django REST framework documentation for description.

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'SecretKey'
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []

TIME_ZONE = 'UTC'
USE_TZ = True
USE_I18N = True
USE_L10N = True

# Must be present when django-guardian (dep. for the REST framework) is installed
ANONYMOUS_USER_ID = -1

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

STATIC_URL = '/static/'
ROOT_URLCONF = 'rdap.urls'

LOG_FILENAME = ''
LOGGING = {
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)-8s - %(message)s',
        },
    },
    'handlers': {
        'dummy': {
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': LOG_FILENAME,
            'mode': 'a',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}



## RDAP Server Settings #######################################################

### CORBA configuration
# Path to the directory with IDL files (absolute path recommended)
CORBA_IDL_ROOT_PATH = ''
# Whois IDL file name
CORBA_IDL_WHOIS_FILENAME = 'Whois2.idl'
# Logger IDL file name
CORBA_IDL_LOGGER_FILENAME = 'Logger.idl'
# Name service address (host[:port])
CORBA_NS_HOST_PORT = ''
# Name service context
CORBA_NS_CONTEXT = 'fred'
# Modules exported for RDAP - Don't change this!
CORBA_EXPORT_MODULES = ['Registry']

### WHOIS URLs configuration
# Base of URLs
RDAP_ROOT_URL = ''
# URL path for domain queries
RDAP_DOMAIN_URL_TMPL        = RDAP_ROOT_URL + "/domain/%(handle)s"
# URL path for entity queries
RDAP_ENTITY_URL_TMPL        = RDAP_ROOT_URL + "/entity/%(handle)s"
# URL path for nameserver queries
RDAP_NAMESERVER_URL_TMPL    = RDAP_ROOT_URL + "/nameserver/%(handle)s"
# URL path for NSSET queries
RDAP_NSSET_URL_TMPL         = RDAP_ROOT_URL + "/fred_nsset/%(handle)s"
# URL path for keyset queries
RDAP_KEYSET_URL_TMPL        = RDAP_ROOT_URL + "/fred_keyset/%(handle)s"
# Unix Whois server address
UNIX_WHOIS_HOST = ''

# Maximum signature lifetime (seconds)
DNS_MAX_SIG_LIFE = 1209600
# File that is included in each response
DISCLAIMER_FILE = ''
