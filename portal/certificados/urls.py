from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from rest_framework.urlpatterns import format_suffix_patterns
from portal.certificados import views
from portal.certificados.forms import EmissaoNv1Tela1Form, EmissaoNv1Tela2Form, EmissaoNv3Tela1Form, EmissaoNv3Tela2Form
from portal.certificados.views import EmissaoNv1WizardView, EmissaoNv3WizardView, EscolhaVoucherView

FORMS_NV1 = [('tela-1', EmissaoNv1Tela1Form), ('tela-2', EmissaoNv1Tela2Form)]
FORMS_NV3 = [('tela-1', EmissaoNv3Tela1Form), ('tela-2', EmissaoNv3Tela2Form)]

urlpatterns = patterns(
    '',
    url(r'^api/v1/ssl-apply/$', views.EmissaoAPIView.as_view()),
    url(r'^api/v1/ssl-replace/$', views.ReemissaoAPIView.as_view()),
    url(r'^api/v1/ssl-revoke/$', views.RevogacaoAPIView.as_view()),
    url(r'^api/v1/ssl-validate-url-csr/$', views.ValidaUrlCSRAPIView.as_view()),
    url(r'^api/v1/get-voucher-data/$', views.VoucherAPIView.as_view()),
    url(r'^api/v1/get-email-whois/$', views.EmailWhoisAPIView.as_view()),

    url(r'^testando-form-ssl/(?P<crm_hash>\w+)/$', login_required(EmissaoNv1WizardView.as_view(form_list=FORMS_NV1)), name='form-nv1'),
    url(r'^testando-form-ev/(?P<crm_hash>\w+)/$', login_required(EmissaoNv3WizardView.as_view(form_list=FORMS_NV3)), name='form-nv3'),
    url(r'^escolha-voucher/$', login_required(EscolhaVoucherView.as_view()), name='escolha_voucher'),
    url(r'^emissao-de-certificado-finalizada/$', TemplateView.as_view(template_name='certificados/sucesso.html'),
        name='certificado_emitido_sucesso')
)

urlpatterns = format_suffix_patterns(urlpatterns)