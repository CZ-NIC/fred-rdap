"""
Django settings for rdap project.
"""
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

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'rest_framework',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

STATIC_URL = '/static/'
ROOT_URLCONF = 'rdap.urls'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rdap.rdap_rest.renderer.RDAPJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_CONTENT_NEGOTIATION_CLASS': 'rdap.rdap_rest.content_negotiation.RdapJsonForAllContentNegotiation',
    'EXCEPTION_HANDLER': 'rdap.rdap_rest.exception_handler.rdap_exception_handler'
}

# CORBA CONFIGURATION
CORBA_IDL_ROOT_PATH = ''
CORBA_IDL_WHOIS_FILENAME = 'Whois2.idl'
CORBA_IDL_LOGGER_FILENAME = 'Logger.idl'
CORBA_NS_HOST_PORT = ''
CORBA_NS_CONTEXT = 'fred'
CORBA_EXPORT_MODULES = ['Registry']

# WHOIS URLS CONFIGURATION
RDAP_ROOT_URL = ''
RDAP_DOMAIN_URL_TMPL        = RDAP_ROOT_URL + "/domain/%(handle)s"
RDAP_ENTITY_URL_TMPL        = RDAP_ROOT_URL + "/entity/%(handle)s"
RDAP_NAMESERVER_URL_TMPL    = RDAP_ROOT_URL + "/nameserver/%(handle)s"
RDAP_NSSET_URL_TMPL         = RDAP_ROOT_URL + "/fred_nsset/%(handle)s"
RDAP_KEYSET_URL_TMPL        = RDAP_ROOT_URL + "/fred_keyset/%(handle)s"
UNIX_WHOIS_HOST = ''

# etc
DNS_MAX_SIG_LIFE = 1209600
DISCLAIMER_FILE = ''

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
