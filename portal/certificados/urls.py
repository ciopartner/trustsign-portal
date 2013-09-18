from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from rest_framework.urlpatterns import format_suffix_patterns
from portal.certificados import views
from portal.certificados.forms import EmissaoNv1Tela1Form, EmissaoNv1Tela2Form, EmissaoNv3Tela1Form, \
    EmissaoNv3Tela2Form, EmissaoNv2Tela2Form, EmissaoNv2Tela1Form, EmissaoNv4Tela1Form, EmissaoNv4Tela2Form, \
    EmissaoNvATela1Form, EmissaoConfirmacaoForm, EmissaoNvBTela1Form
from portal.certificados.views import EmissaoNv1WizardView, EmissaoNv3WizardView, EscolhaVoucherView, \
    EmissaoNv2WizardView, EmissaoNv4WizardView, EmissaoNvAWizardView, EmissaoNvBWizardView

FORMS_NV1 = [('tela-1', EmissaoNv1Tela1Form), ('tela-2', EmissaoNv1Tela2Form), ('tela-confirmacao', EmissaoConfirmacaoForm)]
FORMS_NV2 = [('tela-1', EmissaoNv2Tela1Form), ('tela-2', EmissaoNv2Tela2Form), ('tela-confirmacao', EmissaoConfirmacaoForm)]
FORMS_NV3 = [('tela-1', EmissaoNv3Tela1Form), ('tela-2', EmissaoNv3Tela2Form), ('tela-confirmacao', EmissaoConfirmacaoForm)]
FORMS_NV4 = [('tela-1', EmissaoNv4Tela1Form), ('tela-2', EmissaoNv4Tela2Form), ('tela-confirmacao', EmissaoConfirmacaoForm)]
FORMS_NVA = [('tela-1', EmissaoNvATela1Form), ('tela-confirmacao', EmissaoConfirmacaoForm)]
FORMS_NVB = [('tela-1', EmissaoNvBTela1Form), ('tela-confirmacao', EmissaoConfirmacaoForm)]

urlpatterns = patterns(
    '',
    url(r'^api/v1/ssl-apply/$', views.EmissaoAPIView.as_view()),
    url(r'^api/v1/ssl-replace/$', views.ReemissaoAPIView.as_view()),
    url(r'^api/v1/ssl-revoke/$', views.RevogacaoAPIView.as_view()),
    url(r'^api/v1/ssl-validate-url-csr/$', views.ValidaUrlCSRAPIView.as_view()),
    url(r'^api/v1/get-voucher-data/$', views.VoucherAPIView.as_view()),
    url(r'^api/v1/get-email-whois/$', views.EmailWhoisAPIView.as_view()),

    url(r'^emissao/(ssl|wildcard)/(?P<crm_hash>\w+)/$', login_required(EmissaoNv1WizardView.as_view(form_list=FORMS_NV1)), name='form-nv1'),
    url(r'^emissao/(ssl-san|ssl-mdc)/(?P<crm_hash>\w+)/$', login_required(EmissaoNv2WizardView.as_view(form_list=FORMS_NV2)), name='form-nv2'),
    url(r'^emissao/ssl-ev/(?P<crm_hash>\w+)/$', login_required(EmissaoNv3WizardView.as_view(form_list=FORMS_NV3)), name='form-nv3'),
    url(r'^emissao/ssl-ev-mdc/(?P<crm_hash>\w+)/$', login_required(EmissaoNv4WizardView.as_view(form_list=FORMS_NV4)), name='form-nv4'),
    url(r'^emissao/(ssl-cs|ssl-jre)/(?P<crm_hash>\w+)/$', login_required(EmissaoNvAWizardView.as_view(form_list=FORMS_NVA)), name='form-nvA'),
    url(r'^emissao/ssl-smime/(?P<crm_hash>\w+)/$', login_required(EmissaoNvBWizardView.as_view(form_list=FORMS_NVB)), name='form-nvB'),

    url(r'^escolha-voucher/$', login_required(EscolhaVoucherView.as_view()), name='escolha_voucher'),
    url(r'^emissao-de-certificado-realizada/$', TemplateView.as_view(template_name='certificados/sucesso.html'),
        name='certificado_emitido_sucesso')
)

urlpatterns = format_suffix_patterns(urlpatterns)