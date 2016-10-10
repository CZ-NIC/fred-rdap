from django.conf.urls import patterns, url

from rdap.rdap_rest.views import DomainViewSet, NameserverViewSet
from rdap.rdap_rest.whois import get_contact_by_handle, get_keyset_by_handle, get_nsset_by_handle
from rdap.views import HelpView, ObjectView, UnsupportedView

domain_detail = DomainViewSet.as_view({'get': 'retrieve'})
nameserver_detail = NameserverViewSet.as_view({'get': 'retrieve'})


urlpatterns = patterns(
    '',
    url(r'(?i)^entity/(?P<handle>.+)$',
        ObjectView.as_view(getter=get_contact_by_handle, request_type='EntityLookup'),
        name='entity-detail'),
    url(r'(?i)^(?P<path>domain)/(?P<handle>.+)$', domain_detail, name='domain-detail'),
    url(r'(?i)^(?P<path>nameserver)/(?P<handle>.+)$', nameserver_detail, name='nameserver-detail'),
    url(r'(?i)^fred_nsset/(?P<handle>.+)$',
        ObjectView.as_view(getter=get_nsset_by_handle, request_type='NSSetLookup'),
        name='nsset-detail'),
    url(r'(?i)^fred_keyset/(?P<handle>.+)$',
        ObjectView.as_view(getter=get_keyset_by_handle, request_type='KeySetLookup'),
        name='keyset-detail'),
    url(r'(?i)^autnum/.+$', UnsupportedView.as_view()),
    url(r'(?i)^ip/.+$', UnsupportedView.as_view()),
    url(r'(?i)^domains$', UnsupportedView.as_view()),
    url(r'(?i)^nameservers$', UnsupportedView.as_view()),
    url(r'(?i)^entities$', UnsupportedView.as_view()),
    url(r'(?i)^help$', HelpView.as_view(), name='help'),
    url(r'.*', UnsupportedView.as_view(status=400)),
)
