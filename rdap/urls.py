from django.conf.urls import patterns, url

from rdap.rdap_rest.views import DomainViewSet, EntityViewSet, KeySetViewSet, NameserverViewSet, NSSetViewSet
from rdap.views import HelpView, UnsupportedView

entity_detail = EntityViewSet.as_view({'get': 'retrieve'})
domain_detail = DomainViewSet.as_view({'get': 'retrieve'})
nameserver_detail = NameserverViewSet.as_view({'get': 'retrieve'})
nsset_detail = NSSetViewSet.as_view({'get': 'retrieve'})
keyset_detail = KeySetViewSet.as_view({'get': 'retrieve'})


urlpatterns = patterns(
    '',
    url(r'(?i)^(?P<path>entity)/(?P<handle>.+)$', entity_detail, name='entity-detail'),
    url(r'(?i)^(?P<path>domain)/(?P<handle>.+)$', domain_detail, name='domain-detail'),
    url(r'(?i)^(?P<path>nameserver)/(?P<handle>.+)$', nameserver_detail, name='nameserver-detail'),
    url(r'(?i)^(?P<path>fred_nsset)/(?P<handle>.+)$', nsset_detail, name='nsset-detail'),
    url(r'(?i)^(?P<path>fred_keyset)/(?P<handle>.+)$', keyset_detail, name='keyset-detail'),
    url(r'(?i)^autnum/.+$', UnsupportedView.as_view()),
    url(r'(?i)^ip/.+$', UnsupportedView.as_view()),
    url(r'(?i)^domains$', UnsupportedView.as_view()),
    url(r'(?i)^nameservers$', UnsupportedView.as_view()),
    url(r'(?i)^entities$', UnsupportedView.as_view()),
    url(r'(?i)^help$', HelpView.as_view(), name='help'),
    url(r'.*', UnsupportedView.as_view(status=400)),
)
