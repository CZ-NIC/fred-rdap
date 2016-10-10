import os

INSTALLED_APPS = ()
ROOT_URLCONF = 'rdap.urls'
SECRET_KEY = 'SECRET'

CORBA_IDL_ROOT_PATH = os.environ.get('FRED_IDL_DIR', './idl/idl')
CORBA_IDL_WHOIS_FILENAME = 'Whois2.idl'
CORBA_IDL_LOGGER_FILENAME = 'Logger.idl'
CORBA_NS_HOST_PORT = 'localhost'
CORBA_NS_CONTEXT = 'fred'
CORBA_EXPORT_MODULES = ['Registry']
DISCLAIMER_FILE = ''
RDAP_DOMAIN_URL_TMPL = "/domain/%(handle)s"
RDAP_ENTITY_URL_TMPL = "/entity/%(handle)s"
RDAP_KEYSET_URL_TMPL = "/fred_keyset/%(handle)s"
RDAP_NAMESERVER_URL_TMPL = "/nameserver/%(handle)s"
RDAP_NSSET_URL_TMPL = "/fred_nsset/%(handle)s"
UNIX_WHOIS_HOST = ''
