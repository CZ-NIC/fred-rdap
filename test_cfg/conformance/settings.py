#
# Copyright (C) 2016-2018  CZ.NIC, z. s. p. o.
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
INSTALLED_APPS = ('rdap.apps.RdapAppConfig', )
MIDDLEWARE = ['settings.CorsMiddleware',
              'django.middleware.common.CommonMiddleware']
ROOT_URLCONF = 'rdap.urls'
SECRET_KEY = 'SECRET'

RDAP_ROOT_URL = 'http://localhost:8000'
DNS_MAX_SIG_LIFE = 1209600
