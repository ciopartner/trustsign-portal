from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from rest_framework.urlpatterns import format_suffix_patterns
from portal.certificados import views
from portal.certificados.forms import EmissaoNv1Tela1Form, EmissaoNv1Tela2Form
from portal.certificados.views import EmissaoNv1WizardView

FORMS_NV1 = [('tela-1', EmissaoNv1Tela1Form), ('tela-2', EmissaoNv1Tela2Form)]

urlpatterns = patterns(
    '',
    url(r'^api/v1/emitir-certificado/$', views.EmissaoAPIView.as_view()),
    url(r'^api/v1/reemitir-certificado/$', views.ReemissaoAPIView.as_view()),
    url(r'^api/v1/revogar-certificado/$', views.RevogacaoAPIView.as_view()),
    url(r'^api/v1/validar-url-csr/$', views.ValidaUrlCSRAPIView.as_view()),
    url(r'^api/v1/get-voucher-dados/$', views.VoucherAPIView.as_view()),
    url(r'^api/v1/get-emails-whois/$', views.EmailWhoisAPIView.as_view()),

    url(r'^testando-form-ssl/(?P<crm_hash>\w+)/$',
        login_required(EmissaoNv1WizardView.as_view(form_list=FORMS_NV1))
        ),
    url(r'^emissao-de-certificado-finalizada/$', TemplateView.as_view(template_name='certificados/sucesso.html'),
        name='certificado_emitido_sucesso')
)

urlpatterns = format_suffix_patterns(urlpatterns)