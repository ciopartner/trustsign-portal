# coding=utf-8
import os
from django.contrib.formtools.wizard.views import SessionWizardView
from django.core.exceptions import PermissionDenied
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.views.generic import ListView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.renderers import UnicodeJSONRenderer, BrowsableAPIRenderer
from portal.certificados import comodo
from portal.certificados.authentication import UserPasswordAuthentication
from portal.certificados.models import Emissao, Voucher
from portal.certificados.serializers import EmissaoNv0Serializer, EmissaoNv1Serializer, EmissaoNv2Serializer, \
    EmissaoNv3Serializer, EmissaoNv4Serializer, EmissaoNvASerializer
from django.conf import settings
from portal.ferramentas.utils import verifica_razaosocial_dominio


class EmissaoAPIView(ListModelMixin, CreateModelMixin, GenericAPIView):
    queryset = Emissao.objects.all()
    authentication_classes = [UserPasswordAuthentication]
    renderer_classes = [UnicodeJSONRenderer, BrowsableAPIRenderer]

    def get_serializer_context(self):
        """
        Coloca o usuário no kwargs do init do EmissaoSerializer
        """
        context = super(EmissaoAPIView, self).get_serializer_context()
        context.update({
            'user': self.request.user
        })
        return context

    def get_serializer_class(self):
        voucher = self.get_voucher()
        if voucher.ssl_product in (voucher.PRODUTO_SITE_SEGURO, voucher.PRODUTO_SITE_MONITORADO):
            return EmissaoNv0Serializer
        if voucher.ssl_product in (voucher.PRODUTO_SSL, voucher.PRODUTO_SSL_WILDCARD):
            return EmissaoNv1Serializer
        if voucher.ssl_product in (voucher.PRODUTO_SAN_UCC, voucher.PRODUTO_MDC):
            return EmissaoNv2Serializer
        if voucher.ssl_product == voucher.PRODUTO_EV:
            return EmissaoNv3Serializer
        if voucher.ssl_product == voucher.PRODUTO_EV_MDC:
            return EmissaoNv4Serializer
        if voucher.ssl_product in (voucher.PRODUTO_JRE, voucher.PRODUTO_CODE_SIGNING, voucher.PRODUTO_SMIME):
            return EmissaoNvASerializer
        raise Http404()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_voucher(self):
        try:
            return Voucher.objects.get(crm_hash=self.request.DATA.get('crm_hash'))
        except Voucher.DoesNotExist:
            raise Http404()


class ReemissaoAPIView(ListModelMixin, CreateModelMixin, GenericAPIView):
    #TODO: implementar
    pass


class RevogacaoAPIView(ListModelMixin, CreateModelMixin, GenericAPIView):
    #TODO: implementar
    pass


class EmailWhoisAPIView(GenericAPIView):
    #TODO: implementar
    pass


class VoucherAPIView(GenericAPIView):
    #TODO: implementar
    pass


class ValidaUrlCSRAPIView(GenericAPIView):
    #TODO: implementar
    pass


class EscolhaVoucherView(ListView):
    template_name = 'certificados/escolha_voucher.html'
    model = Voucher
    context_object_name = 'vouchers'

    def get_queryset(self):
        return Voucher.objects.select_related('emissao').filter(
            Q(emissao__isnull=True) | Q(emissao__emissao_status__in=(
                Emissao.STATUS_NAO_EMITIDO, Emissao.STATUS_EMITIDO,
                Emissao.STATUS_EM_EMISSAO, Emissao.STATUS_ACAO_MANUAL_PENDENTE
            ))).filter(
                customer_cnpj=self.request.user.username
            )


class EmissaoWizardView(SessionWizardView):
    model = Emissao
    done_redirect_url = 'certificado_emitido_sucesso'
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'forms'))
    template_name = 'base.html'
    templates = {}
    _voucher = None

    # para verificar se precisa de carta de cessao:
    tela_emissao_url = 'tela-1'  # usado para encontrar o form que vai exibir o campo emission_url
    tela_carta_cessao = 'tela-2'  # usado para encontrar o form que vai exibir o campo emission_assignment_letter

    produtos_voucher = ()

    def dispatch(self, request, *args, **kwargs):
        self.instance = self.model()
        self._precisa_carta_cessao = {}
        if Emissao.objects.filter(crm_hash=self.kwargs['crm_hash']).exists():
            raise Http404()  # Não é possível emitir duas vezes o mesmo voucher

        voucher = self.get_voucher()
        if voucher.ssl_product not in self.produtos_voucher:
            raise Http404()
        user = self.request.user
        if voucher.customer_cnpj != user.username and not user.is_superuser:
            # TODO: TBD > precisa validar também se o usuario esta no grupo com permissao(trust)
            raise PermissionDenied()

        return super(EmissaoWizardView, self).dispatch(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        self.precisa_carta_cessao(self.steps.current)
        return super(EmissaoWizardView, self).post(*args, **kwargs)

    def get_form_instance(self, step):
        return self.instance

    def done(self, form_list, **kwargs):
        self.save(form_list, **kwargs)
        return HttpResponseRedirect(reverse(self.done_redirect_url))

    def save(self, form_list, **kwargs):
        self.instance.save()

    def get_form_initial(self, step):
        initial = super(EmissaoWizardView, self).get_form_initial(step)

        if step == 'tela-1':
            voucher = self.get_voucher()
            initial.update({
                'callback_tratamento': voucher.customer_callback_title,
                'callback_nome': voucher.customer_callback_firstname,
                'callback_sobrenome': voucher.customer_callback_lastname,
                'callback_email': voucher.customer_callback_email,
                'callback_telefone': voucher.customer_callback_phone,
                'callback_observacao': voucher.customer_callback_note,
                'callback_username': voucher.customer_callback_username,
            })
        elif step == 'tela-2':
            cd = self.get_cleaned_data_for_step('tela-1')
            initial['emission_url'] = cd['emission_url']
            initial['emission_csr'] = cd['emission_csr']
        return initial

    def get_form_kwargs(self, step=None):
        kwargs = super(EmissaoWizardView, self).get_form_kwargs(step)
        kwargs['user'] = self.request.user
        kwargs['crm_hash'] = self.kwargs['crm_hash']
        kwargs['voucher'] = self.get_voucher()
        kwargs['precisa_carta_cessao'] = self._precisa_carta_cessao.get(self.steps.current, False)
        return kwargs

    def get_context_data(self, form, **kwargs):
        context = super(EmissaoWizardView, self).get_context_data(form, **kwargs)
        context.update({
            'voucher': self.get_voucher(),
            'precisa_carta_cessao': self.precisa_carta_cessao(self.steps.current)
        })
        return context

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def get_voucher(self):
        if not self._voucher:
            try:
                self._voucher = Voucher.objects.get(crm_hash=self.kwargs.get('crm_hash'))
            except Voucher.DoesNotExist:
                raise Http404()
        return self._voucher

    def precisa_carta_cessao(self, step):
        if self._precisa_carta_cessao.get(step) is None:
            if self.steps.current == self.tela_carta_cessao:
                cleaned_data = self.get_cleaned_data_for_step(self.tela_emissao_url) or {}

                voucher = self.get_voucher()
                self._precisa_carta_cessao[step] = not verifica_razaosocial_dominio(
                    voucher.customer_companyname,
                    cleaned_data['emission_url']
                )

            else:
                self._precisa_carta_cessao[step] = False

        return self._precisa_carta_cessao[step]

    def save(self, form_list, **kwargs):
        emissao = self.instance
        emissao.solicitante_user_id = self.request.user.pk
        emissao.crm_hash = self.kwargs['crm_hash']

        voucher = self.get_voucher()
        emissao.voucher = voucher

        self.atualiza_voucher(voucher)

        if any(f.validacao_manual for f in form_list):
            emissao.emission_status = emissao.STATUS_ACAO_MANUAL_PENDENTE
        else:
            emissao.emission_status = emissao.STATUS_EM_EMISSAO
            resposta = comodo.emite_certificado(emissao)

            emissao.comodo_order = resposta['orderNumber']
            emissao.emission_cost = resposta['totalCost']
        emissao.save()

    def atualiza_voucher(self, voucher):
        dados_voucher = self.get_cleaned_data_for_step('tela-1')

        v = dados_voucher.get('callback_tratamento')
        if v:
            voucher.customer_callback_title = v

        v = dados_voucher.get('callback_nome')
        if v:
            voucher.customer_callback_firstname = v

        v = dados_voucher.get('callback_sobrenome')
        if v:
            voucher.customer_callback_lastname = v

        v = dados_voucher.get('callback_email')
        if v:
            voucher.customer_callback_email = v

        v = dados_voucher.get('callback_telefone')
        if v:
            voucher.customer_callback_phone = v

        v = dados_voucher.get('callback_observacao')
        if v:
            voucher.customer_callback_note = v

        v = dados_voucher.get('callback_username')
        if v:
            voucher.customer_callback_username = v

        v = dados_voucher.get('callback_password')
        if v:
            voucher.customer_callback_password = v


class EmissaoNv1WizardView(EmissaoWizardView):
    produtos_voucher = (Voucher.PRODUTO_SSL, Voucher.PRODUTO_SSL_WILDCARD)
    templates = {
        'tela-1': 'certificados/wizard_nv1_tela_1.html',
        'tela-2': 'certificados/wizard_nv1_tela_2.html',
        'tela-confirmacao': 'certificados/wizard_nv1_confirmacao.html'
    }


class EmissaoNv2WizardView(EmissaoWizardView):
    produtos_voucher = (Voucher.PRODUTO_SAN_UCC, Voucher.PRODUTO_MDC)
    templates = {
        'tela-1': 'certificados/wizard_nv2_tela_1.html',
        'tela-2': 'certificados/wizard_nv2_tela_2.html',
        'tela-confirmacao': 'certificados/wizard_nv2_confirmacao.html'
    }


class EmissaoNv3WizardView(EmissaoWizardView):
    produtos_voucher = (Voucher.PRODUTO_EV,)
    templates = {
        'tela-1': 'certificados/wizard_nv3_tela_1.html',
        'tela-2': 'certificados/wizard_nv3_tela_2.html',
        'tela-confirmacao': 'certificados/wizard_nv3_confirmacao.html'
    }


class EmissaoNv4WizardView(EmissaoWizardView):
    produtos_voucher = (Voucher.PRODUTO_EV_MDC,)
    templates = {
        'tela-1': 'certificados/wizard_nv4_tela_1.html',
        'tela-2': 'certificados/wizard_nv4_tela_2.html',
        'tela-confirmacao': 'certificados/wizard_nv4_confirmacao.html'
    }


class EmissaoNvAWizardView(EmissaoWizardView):
    produtos_voucher = (Voucher.PRODUTO_JRE, Voucher.PRODUTO_CODE_SIGNING)
    templates = {
        'tela-1': 'certificados/wizard_nvA_tela_1.html',
        'tela-confirmacao': 'certificados/wizard_nvA_confirmacao.html'
    }


class EmissaoNvBWizardView(EmissaoWizardView):
    produtos_voucher = (Voucher.PRODUTO_SMIME,)
    templates = {
        'tela-1': 'certificados/wizard_nvB_tela_1.html',
        'tela-confirmacao': 'certificados/wizard_nvB_confirmacao.html'
    }