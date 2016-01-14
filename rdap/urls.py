from django.conf.urls import patterns, include, url

from rdap.rdap_rest.views import DomainViewSet, EntityViewSet, KeySetViewSet, MalformedRdapPathViewSet, \
    NameserverViewSet, NSSetViewSet, UnsupportedViewSet, HelpViewSet


entity_detail = EntityViewSet.as_view({'get': 'retrieve'})
domain_detail = DomainViewSet.as_view({'get': 'retrieve'})
nameserver_detail = NameserverViewSet.as_view({'get': 'retrieve'})
nsset_detail = NSSetViewSet.as_view({'get': 'retrieve'})
keyset_detail = KeySetViewSet.as_view({'get': 'retrieve'})
malformed_rdap_path = MalformedRdapPathViewSet.as_view({'get': 'retrieve'})
unsupported = UnsupportedViewSet.as_view({'get': 'retrieve'})
help_page = HelpViewSet.as_view({'get': 'retrieve'})


urlpatterns = patterns('',
    url(r'(?i)^(?P<path>entity)/(?P<handle>.+)$', entity_detail, name='entity-detail'),
    url(r'(?i)^(?P<path>domain)/(?P<handle>.+)$', domain_detail, name='domain-detail'),
    url(r'(?i)^(?P<path>nameserver)/(?P<handle>.+)$', nameserver_detail, name='nameserver-detail'),
    url(r'(?i)^(?P<path>cznic_nsset)/(?P<handle>.+)$', nsset_detail, name='nsset-detail'),
    url(r'(?i)^(?P<path>cznic_keyset)/(?P<handle>.+)$', keyset_detail, name='keyset-detail'),
    url(r'(?i)^(?P<path>autnum|ip)/.+', unsupported, name='unsupported'),
    url(r'(?i)^help$', help_page, name='help'),
    url(r'.*', malformed_rdap_path, name='malformed-path-view'),
)
