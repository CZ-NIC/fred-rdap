#
# Copyright (C) 2014-2022  CZ.NIC, z. s. p. o.
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
from django.urls import path, re_path

from rdap.rdap_rest.whois import (get_contact_by_handle, get_domain_by_handle, get_keyset_by_handle,
                                  get_nameserver_by_handle, get_nsset_by_handle)
from rdap.views import FqdnObjectView, HelpView, ObjectView, UnsupportedView

from .constants import LogEntryType

urlpatterns = [
    path('entity/<handle>',
         ObjectView.as_view(getter=get_contact_by_handle, request_type=LogEntryType.ENTITY_LOOKUP),
         name='entity-detail'),
    path('domain/<handle>',
         FqdnObjectView.as_view(getter=get_domain_by_handle, request_type=LogEntryType.DOMAIN_LOOKUP),
         name='domain-detail'),
    path('nameserver/<handle>',
         FqdnObjectView.as_view(getter=get_nameserver_by_handle, request_type=LogEntryType.NAMESERVER_LOOKUP),
         name='nameserver-detail'),
    path('fred_nsset/<handle>',
         ObjectView.as_view(getter=get_nsset_by_handle, request_type=LogEntryType.NSSET_LOOKUP),
         name='nsset-detail'),
    path('fred_keyset/<handle>',
         ObjectView.as_view(getter=get_keyset_by_handle, request_type=LogEntryType.KEYSET_LOOKUP),
         name='keyset-detail'),
    re_path(r'^autnum/.+$', UnsupportedView.as_view()),
    re_path(r'^ip/.+$', UnsupportedView.as_view()),
    path('domains', UnsupportedView.as_view()),
    path('nameservers', UnsupportedView.as_view()),
    path('entities', UnsupportedView.as_view()),
    path('help', HelpView.as_view(), name='help'),
    re_path(r'.*', UnsupportedView.as_view(status=400)),
]
