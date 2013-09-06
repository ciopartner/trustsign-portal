from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from portal.certificados import views

urlpatterns = patterns(
    '',
    url(r'^api/v1/emitir-certificado/(?P<tipo>site-seguro|site-monitorado)/$', views.EmissaoNv0List.as_view()),
    url(r'^api/v1/emitir-certificado/(?P<tipo>ssl|wildcard-ssl)/$', views.EmissaoNv1List.as_view()),
    url(r'^api/v1/emitir-certificado/(?P<tipo>san-ssl|mdc-ssl)/$', views.EmissaoNv2List.as_view()),
    url(r'^api/v1/emitir-certificado/(?P<tipo>ev-ssl)/$', views.EmissaoNv3List.as_view()),
    url(r'^api/v1/emitir-certificado/(?P<tipo>ev-mdc-ssl)/$', views.EmissaoNv4List.as_view()),
    url(r'^api/v1/emitir-certificado/(?P<tipo>code-signing|jre)/$', views.EmissaoNvAList.as_view()),
    url(r'^api/v1/revogar-certificado/$', views.EmissaoNvAList.as_view()),
    url(r'^api/v1/reemitir-certificado/$', views.EmissaoNvAList.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns)