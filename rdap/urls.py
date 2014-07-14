from django.conf.urls import patterns, include, url
from rest_framework import routers

from rdap.rdap_rest.views import DomainViewSet, EntityViewSet, KeySetViewSet, MalformedRdapPath, NameserverViewSet, \
    NotFound, NSSetViewSet


entity_detail = EntityViewSet.as_view({'get': 'retrieve'})
domain_detail = DomainViewSet.as_view({'get': 'retrieve'})
nameserver_detail = NameserverViewSet.as_view({'get': 'retrieve'})
nsset_detail = NSSetViewSet.as_view({'get': 'retrieve'})
keyset_detail = KeySetViewSet.as_view({'get': 'retrieve'})
malformed_rdap_path = MalformedRdapPath.as_view({'get': 'retrieve'})
not_found = NotFound.as_view({'get': 'retrieve'})


urlpatterns = patterns('',
    url(r'(?i)^(?P<path>entity)/(?P<handle>[A-Z0-9_\:\.\-]{1,255})$', entity_detail, name='entity-detail'),
    url(r'(?i)^(?P<path>domain)/(?P<handle>[A-Z0-9_\.\-]{1,255})$', domain_detail, name='domain-detail'),
    url(r'(?i)^(?P<path>nameserver)/(?P<handle>[A-Z0-9_\.\-]{1,255})$', nameserver_detail, name='nameserver-detail'),
    url(r'(?i)^(?P<path>cznic_nsset)/(?P<handle>[A-Z0-9_\:\.\-]{1,255})$', nsset_detail, name='nsset-detail'),
    url(r'(?i)^(?P<path>cznic_keyset)/(?P<handle>[A-Z0-9_\:\.\-]{1,255})$', keyset_detail, name='keyset-detail'),
    url(r'(?i)^(?P<path>(entity|domain|nameserver|cznic_nsset|cznic_keyset))/(?P<handle>.+)$', not_found,
        name='not-found'),
    url(r'.*', malformed_rdap_path, name='malformed-path-view'),
)
