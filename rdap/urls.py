from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

# urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'rdap.views.home', name='home'),
    # url(r'^rdap/', include('rdap.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
# )

from rest_framework import routers
from rdap_rest import views


entity_detail = views.EntityViewSet.as_view({
    'get': 'retrieve'
})


entity_list = views.EntityViewSet.as_view({
    'get': 'list'
})


urlpatterns = patterns('',
    url(r'(?i)^entity/(?P<handle>[A-Z0-9_\:\.\-]{1,255})$', entity_detail, name='entity-detail'),
    url(r'(?i)^entities/$', entity_list, name='entity-list'),
)

