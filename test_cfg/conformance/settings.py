class CorsMiddleware(object):
    """Middleware to add CORS header to every response.

    Workaround for the bug reported to RDAP conformance tests https://github.com/APNIC-net/rdap-conformance/issues/41.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Access-Control-Allow-Origin'] = '*'
        return response


DEBUG = False
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = ()
MIDDLEWARE = ['settings.CorsMiddleware',
              'django.middleware.common.CommonMiddleware']
ROOT_URLCONF = 'rdap.urls'
SECRET_KEY = 'SECRET'

CORBA_NS_HOST_PORT = 'localhost'
CORBA_NS_CONTEXT = 'fred'
RDAP_ROOT_URL = 'http://localhost:8000'
DNS_MAX_SIG_LIFE = 1209600
DISCLAIMER_FILE = ''
UNIX_WHOIS_HOST = 'whois.nic.cz'
