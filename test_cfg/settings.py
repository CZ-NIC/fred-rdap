import os

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'rest_framework',
)
SECRET_KEY = 'SECRET'

CORBA_IDL_ROOT_PATH = os.environ.get('FRED_IDL_DIR', './idl/idl')
CORBA_IDL_WHOIS_FILENAME = 'Whois2.idl'
CORBA_IDL_LOGGER_FILENAME = 'Logger.idl'
CORBA_NS_HOST_PORT = 'localhost'
CORBA_NS_CONTEXT = 'fred'
CORBA_EXPORT_MODULES = ['Registry']
