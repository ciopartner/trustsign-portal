# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from rest_framework.urlpatterns import format_suffix_patterns
from portal.certificados import views
from portal.certificados.forms import EmissaoNv1Tela1Form, EmissaoNv1Tela2Form, EmissaoNv3Tela1Form, \
    EmissaoNv3Tela2Form, EmissaoNv2Tela2Form, EmissaoNv2Tela1Form, EmissaoNv4Tela1Form, EmissaoNv4Tela2Form, \
    EmissaoNvATela1Form, EmissaoConfirmacaoForm, EmissaoNvBTela1Form
from portal.certificados.models import Voucher
from portal.certificados.views import EmissaoNv1WizardView, EmissaoNv3WizardView, EscolhaVoucherView, \
    EmissaoNv2WizardView, EmissaoNv4WizardView, EmissaoNvAWizardView, EmissaoNvBWizardView, RevogacaoView, \
    ReemissaoView, RevisaoEmissaoNv1WizardView, RevisaoEmissaoNv2WizardView, RevisaoEmissaoNv3WizardView, \
    RevisaoEmissaoNv4WizardView, RevisaoEmissaoNvAWizardView, RevisaoEmissaoNvBWizardView, VouchersPendentesListView, AprovaVoucherPendenteView

FORMS_NV1 = [('tela-1', EmissaoNv1Tela1Form), ('tela-2', EmissaoNv1Tela2Form), ('tela-confirmacao', EmissaoConfirmacaoForm)]
FORMS_NV2 = [('tela-1', EmissaoNv2Tela1Form), ('tela-2', EmissaoNv2Tela2Form), ('tela-confirmacao', EmissaoConfirmacaoForm)]
FORMS_NV3 = [('tela-1', EmissaoNv3Tela1Form), ('tela-2', EmissaoNv3Tela2Form), ('tela-confirmacao', EmissaoConfirmacaoForm)]
FORMS_NV4 = [('tela-1', EmissaoNv4Tela1Form), ('tela-2', EmissaoNv4Tela2Form), ('tela-confirmacao', EmissaoConfirmacaoForm)]
FORMS_NVA = [('tela-1', EmissaoNvATela1Form), ('tela-confirmacao', EmissaoConfirmacaoForm)]
FORMS_NVB = [('tela-1', EmissaoNvBTela1Form), ('tela-confirmacao', EmissaoConfirmacaoForm)]

urlpatterns = patterns(
    '',
    url(r'^api/v1/ssl-apply/$', csrf_exempt(views.EmissaoAPIView.as_view())),
    url(r'^api/v1/ssl-replace/$', csrf_exempt(views.ReemissaoAPIView.as_view())),
    url(r'^api/v1/ssl-revoke/$', csrf_exempt(views.RevogacaoAPIView.as_view())),
    url(r'^api/v1/ssl-validate-url-csr/$', csrf_exempt(views.ValidaUrlCSRAPIView.as_view())),
    url(r'^api/v1/ssl-voucher-create/$', csrf_exempt(views.VoucherCreateAPIView.as_view())),
    url(r'^api/v1/get-voucher-data/$', csrf_exempt(views.VoucherAPIView.as_view()), name='api_get_voucher_data'),
    url(r'^api/v1/get-email-whois/$', csrf_exempt(views.EmailWhoisAPIView.as_view())),

    url(r'^emissao/(%s|%s)/(?P<crm_hash>\w+)/$' % (Voucher.PRODUTO_SSL, Voucher.PRODUTO_SSL_WILDCARD), login_required(EmissaoNv1WizardView.as_view(form_list=FORMS_NV1)), name='form-emissao-nv1'),
    url(r'^emissao/(%s|%s)/(?P<crm_hash>\w+)/$' % (Voucher.PRODUTO_SAN_UCC, Voucher.PRODUTO_MDC), login_required(EmissaoNv2WizardView.as_view(form_list=FORMS_NV2)), name='form-emissao-nv2'),
    url(r'^emissao/(%s)/(?P<crm_hash>\w+)/$' % Voucher.PRODUTO_EV, login_required(EmissaoNv3WizardView.as_view(form_list=FORMS_NV3)), name='form-emissao-nv3'),
    url(r'^emissao/(%s)/(?P<crm_hash>\w+)/$' % Voucher.PRODUTO_EV_MDC, login_required(EmissaoNv4WizardView.as_view(form_list=FORMS_NV4)), name='form-emissao-nv4'),
    url(r'^emissao/(%s|%s)/(?P<crm_hash>\w+)/$' % (Voucher.PRODUTO_CODE_SIGNING, Voucher.PRODUTO_JRE), login_required(EmissaoNvAWizardView.as_view(form_list=FORMS_NVA)), name='form-emissao-nvA'),
    url(r'^emissao/(%s)/(?P<crm_hash>\w+)/$' % Voucher.PRODUTO_SMIME, login_required(EmissaoNvBWizardView.as_view(form_list=FORMS_NVB)), name='form-emissao-nvB'),

    url(r'^revisao-emissao/(%s|%s)/(?P<crm_hash>\w+)/$' % (Voucher.PRODUTO_SSL, Voucher.PRODUTO_SSL_WILDCARD), login_required(RevisaoEmissaoNv1WizardView.as_view(form_list=FORMS_NV1)), name='form-revisao-emissao-nv1'),
    url(r'^revisao-emissao/(%s|%s)/(?P<crm_hash>\w+)/$' % (Voucher.PRODUTO_SAN_UCC, Voucher.PRODUTO_MDC), login_required(RevisaoEmissaoNv2WizardView.as_view(form_list=FORMS_NV2)), name='form-revisao-emissao-nv2'),
    url(r'^revisao-emissao/(%s)/(?P<crm_hash>\w+)/$' % Voucher.PRODUTO_EV, login_required(RevisaoEmissaoNv3WizardView.as_view(form_list=FORMS_NV3)), name='form-revisao-emissao-nv3'),
    url(r'^revisao-emissao/(%s)/(?P<crm_hash>\w+)/$' % Voucher.PRODUTO_EV_MDC, login_required(RevisaoEmissaoNv4WizardView.as_view(form_list=FORMS_NV4)), name='form-revisao-emissao-nv4'),
    url(r'^revisao-emissao/(%s|%s)/(?P<crm_hash>\w+)/$' % (Voucher.PRODUTO_CODE_SIGNING, Voucher.PRODUTO_JRE), login_required(RevisaoEmissaoNvAWizardView.as_view(form_list=FORMS_NVA)), name='form-revisao-emissao-nvA'),
    url(r'^revisao-emissao/(%s)/(?P<crm_hash>\w+)/$' % Voucher.PRODUTO_SMIME, login_required(RevisaoEmissaoNvBWizardView.as_view(form_list=FORMS_NVB)), name='form-revisao-emissao-nvB'),

    url(r'^revogacao/(?P<crm_hash>\w+)/$', login_required(RevogacaoView.as_view()), name='form-revogacao'),

    url(r'^reemissao/(?P<crm_hash>\w+)/$', login_required(ReemissaoView.as_view()), name='form-reemissao'),

    url(r'^escolha-voucher/$', login_required(EscolhaVoucherView.as_view()), name='escolha-voucher'),
    url(r'^vouchers-pendentes/$', login_required(VouchersPendentesListView.as_view()), name='voucher-pendentes-lista'),
    url(r'^aprova-vouchers-pendente/(?P<crm_hash>\w+)/$', login_required(AprovaVoucherPendenteView.as_view()), name='aprova-voucher-pendente'),
    url(r'^emissao-de-certificado-realizada/$', TemplateView.as_view(template_name='certificados/sucesso.html'),
        name='certificado_emitido_sucesso'),

)

urlpatterns = format_suffix_patterns(urlpatterns)