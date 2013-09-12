from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from portal.certificados import views
from portal.certificados.forms import show_nv0_tela2_condition, EmissaoNv1Tela1Form, EmissaoNv1Tela2Form
from portal.certificados.views import EmissaoNv1WizardView

urlpatterns = patterns(
    '',
    url(r'^api/v1/emitir-certificado/$', views.EmissaoAPIView.as_view()),
    url(r'^api/v1/reemitir-certificado/$', views.ReemissaoAPIView.as_view()),
    url(r'^api/v1/revogar-certificado/$', views.RevogacaoAPIView.as_view()),
    url(r'^api/v1/validar-url-csr/$', views.ValidaUrlCSRAPIView.as_view()),
    url(r'^api/v1/get-voucher-dados/$', views.VoucherAPIView.as_view()),
    url(r'^api/v1/get-emails-whois/$', views.VoucherAPIView.as_view()),

    url(r'^testando-form-ssl/(?P<crm_hash>\w+)/$', EmissaoNv1WizardView.as_view(
        form_list=[('tela-1', EmissaoNv1Tela1Form), ('tela-2', EmissaoNv1Tela2Form)],
        condition_dict={
            'tela-2': show_nv0_tela2_condition
        })
    )
)

urlpatterns = format_suffix_patterns(urlpatterns)