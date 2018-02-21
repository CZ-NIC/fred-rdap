from __future__ import unicode_literals

from django.conf.urls import url

from rdap.rdap_rest.whois import get_contact_by_handle, get_domain_by_handle, get_keyset_by_handle, \
    get_nameserver_by_handle, get_nsset_by_handle
from rdap.views import FqdnObjectView, HelpView, ObjectView, UnsupportedView

urlpatterns = [
    url(r'^(?i)entity/(?P<handle>.+)$',
        ObjectView.as_view(getter=get_contact_by_handle, request_type='EntityLookup'),
        name='entity-detail'),
    url(r'^(?i)domain/(?P<handle>.+)$',
        FqdnObjectView.as_view(getter=get_domain_by_handle, request_type='DomainLookup'),
        name='domain-detail'),
    url(r'^(?i)nameserver/(?P<handle>.+)$',
        FqdnObjectView.as_view(getter=get_nameserver_by_handle, request_type='NameserverLookup'),
        name='nameserver-detail'),
    url(r'^(?i)fred_nsset/(?P<handle>.+)$',
        ObjectView.as_view(getter=get_nsset_by_handle, request_type='NSSetLookup'),
        name='nsset-detail'),
    url(r'^(?i)fred_keyset/(?P<handle>.+)$',
        ObjectView.as_view(getter=get_keyset_by_handle, request_type='KeySetLookup'),
        name='keyset-detail'),
    url(r'^(?i)autnum/.+$', UnsupportedView.as_view()),
    url(r'^(?i)ip/.+$', UnsupportedView.as_view()),
    url(r'^(?i)domains$', UnsupportedView.as_view()),
    url(r'^(?i)nameservers$', UnsupportedView.as_view()),
    url(r'^(?i)entities$', UnsupportedView.as_view()),
    url(r'^(?i)help$', HelpView.as_view(), name='help'),
    url(r'.*', UnsupportedView.as_view(status=400)),
]
