from django.conf.urls import patterns, include, url
from apps.app import application

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ecommerce.views.home', name='home'),
    # url(r'^ecommerce/', include('ecommerce.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^ecommerce/admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^ecommerce/admin/', include(admin.site.urls)),
    ('^ecommerce/', include('website.urls')),
    ('^ecommerce/', include('ecommerce.certificados.urls')),

    (r'^ecommerce/accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/portal/'}),

    (r'^ecommerce/', include(application.urls))
)
