"""
Django settings for rdap project.
"""
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'SecretKey'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []

TIME_ZONE = 'Europe/Prague'
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
        'rest_framework.renderers.UnicodeJSONRenderer',
        'rdap.rdap_rest.renderer.UnicodeRDAPJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_CONTENT_NEGOTIATION_CLASS': 'rdap.rdap_rest.content_negotiation.RdapJsonForAllContentNegotiation',
}

# CORBA CONFIGURATION
CORBA_IDL_ROOT_PATH = ''
CORBA_IDL_WHOIS_FILENAME = ''
CORBA_IDL_LOGGER_FILENAME = ''
CORBA_NS_HOST_PORT = ''
CORBA_NS_CONTEXT = ''
CORBA_EXPORT_MODULES = ['']

# WHOIS URLS CONFIGURATION
RDAP_ROOT_URL = ''
RDAP_DOMAIN_URL_TMPL        = RDAP_ROOT_URL + "/domain/%(handle)s"
RDAP_ENTITY_URL_TMPL        = RDAP_ROOT_URL + "/entity/%(handle)s"
RDAP_NAMESERVER_URL_TMPL    = RDAP_ROOT_URL + "/nameserver/%(handle)s"
RDAP_NSSET_URL_TMPL         = RDAP_ROOT_URL + "/cznic_nsset/%(handle)s"
RDAP_KEYSET_URL_TMPL        = RDAP_ROOT_URL + "/cznic_keyset/%(handle)s"
UNIX_WHOIS_HOST = ''

# etc
DNS_MAX_SIG_LIFE = 1209600
