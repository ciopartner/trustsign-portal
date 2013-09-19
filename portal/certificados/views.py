# coding=utf-8
import os
from django.contrib.formtools.wizard.views import SessionWizardView
from django.core.exceptions import PermissionDenied
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.views.generic import ListView
from rest_framework import status
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin
from rest_framework.renderers import UnicodeJSONRenderer
from rest_framework.response import Response
from portal.certificados import comodo
from portal.certificados.authentication import UserPasswordAuthentication
from portal.certificados.models import Emissao, Voucher, Revogacao
from portal.certificados.serializers import EmissaoNv0Serializer, EmissaoNv1Serializer, EmissaoNv2Serializer, \
    EmissaoNv3Serializer, EmissaoNv4Serializer, EmissaoNvASerializer, VoucherSerializer, RevogacaoSerializer, \
    ReemissaoSerializer
from django.conf import settings


def erro_rest(*erros):
    """
    Cria o Response com o padrão:
    {
        'errors': [ {'code':X, 'message': Y}, {'code':A, 'message': B},]
    }

    onde a chamada seria erro_rest((X,Y), (A,B))
    """
    return Response({
        'errors': [{'code': e[0], 'message': e[1]} for e in erros]
    })


class EmissaoAPIView(CreateModelMixin, GenericAPIView):
    queryset = Emissao.objects.all()
    authentication_classes = [UserPasswordAuthentication]
    renderer_classes = [UnicodeJSONRenderer]

    def get_serializer_context(self):
        """
        Coloca o usuário no kwargs do init do EmissaoSerializer
        """
        context = super(EmissaoAPIView, self).get_serializer_context()
        context.update({
            'user': self.request.user
        })
        return context

    def perform_authentication(self, request):
        pass

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

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)

        if serializer.is_valid():

            emissao = serializer.object
            emissao.requestor_user_id = self.request.user.pk
            emissao.crm_hash = request.DATA.get('crm_hash')

            voucher = self.get_voucher()
            emissao.voucher = voucher

            # self.atualiza_voucher(voucher) TODO: TBD > o que fazer com os dados do voucher

            if serializer.validacao_manual:
                emissao.emission_status = emissao.STATUS_ACAO_MANUAL_PENDENTE
            else:
                emissao.emission_status = emissao.STATUS_EM_EMISSAO
                resposta = comodo.emite_certificado(emissao)

                emissao.comodo_order = resposta['orderNumber']
                emissao.emission_cost = resposta['totalCost']

            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)
            return Response({}, status=status.HTTP_200_OK)
        # errors = {
        #     'errors': serializer.errors
        # }
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_voucher(self):
        try:
            return Voucher.objects.get(crm_hash=self.request.DATA.get('crm_hash'))
        except Voucher.DoesNotExist:
            raise Http404()


class ReemissaoAPIView(ListModelMixin, CreateModelMixin, GenericAPIView):
    model = Emissao
    authentication_classes = [UserPasswordAuthentication]
    renderer_classes = [UnicodeJSONRenderer]
    serializer_class = ReemissaoSerializer

    def post(self, request, *args, **kwargs):
        emissao = get_object_or_404(Emissao.objects, crm_hash=request.DATA.get('crm_hash'))
        serializer = self.get_serializer(data=request.DATA, files=request.FILES, instance=emissao)

        if serializer.is_valid():

            emissao = serializer.object

            resposta = comodo.reemite_certificado(emissao)

            emissao.comodo_order = resposta['orderNumber']
            emissao.emission_cost = resposta['totalCost']

            emissao.id = None  # isso obriga o django a criar um novo objeto

            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)

            headers = self.get_success_headers(serializer.data)
            return Response({}, status=status.HTTP_200_OK, headers=headers)
        # errors = {
        #     'errors': serializer.errors
        # }
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RevogacaoAPIView(CreateModelMixin, GenericAPIView):
    model = Revogacao
    authentication_classes = [UserPasswordAuthentication]
    renderer_classes = [UnicodeJSONRenderer]
    serializer_class = RevogacaoSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)

        if serializer.is_valid():

            revogacao = serializer.object
            revogacao.emissao = get_object_or_404(Emissao.objects, crm_hash=self.request.DATA.get('crm_hash'))

            comodo.revoga_certificado(revogacao)

            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)

            headers = self.get_success_headers(serializer.data)
            return Response({}, status=status.HTTP_201_CREATED, headers=headers)
        # errors = {
        #     'errors': serializer.errors
        # }
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailWhoisAPIView(GenericAPIView):
    authentication_classes = [UserPasswordAuthentication]
    renderer_classes = [UnicodeJSONRenderer]

    def get(self, request, *args, **kwargs):
        try:
            url = request.GET.get('emission_url')
            if not url:
                return erro_rest(('1321', 'Campo emission_url requerido'))  # TODO: codigo erro
            return Response({
                'email_list': comodo.get_emails_validacao(url)
            })
        except Exception:
            return erro_rest(('-1', 'Erro interno do servidor'))


class VoucherAPIView(RetrieveModelMixin, GenericAPIView):
    authentication_classes = [UserPasswordAuthentication]
    renderer_classes = [UnicodeJSONRenderer]
    serializer_class = VoucherSerializer

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(self.object)
        data = serializer.data

        novo = {'contact': {}, 'customer': {}, 'product': {}, 'order': {}}
        for k, v in data.iteritems():
            if k.startswith('customer_callback'):
                novo['contact'][k] = v
            elif k.startswith('customer'):
                novo['customer'][k] = v
            elif k.startswith('ssl'):
                novo['product'][k] = v
            elif k.startswith('order'):
                novo['order'][k] = v
            else:
                novo[k] = v
        return Response(novo)

    def get_object(self, queryset=None):
        obj = get_object_or_404(Voucher.objects, crm_hash=self.request.GET.get('crm_hash'))

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class ValidaUrlCSRAPIView(EmissaoAPIView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)

        if serializer.is_valid():
            data = {
                'required_fields': serializer.REQUIRED_FIELDS,
                'emission_dcv_emails': ['admin', 'postmaster', 'webmaster', 'administrator', 'hostmaster'],
                'server_list': Emissao.SERVIDOR_TIPO_CHOICES
            }
            return Response(data, status=status.HTTP_200_OK)
        # errors = {
        #     'errors': serializer.errors
        # }
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EscolhaVoucherView(ListView):
    template_name = 'certificados/escolha_voucher.html'
    model = Voucher
    context_object_name = 'vouchers'

    def get_queryset(self):
        return Voucher.objects.select_related('emissao').filter(
            Q(emissao__isnull=True) | Q(emissao__emission_status__in=(
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
        return kwargs

    def get_context_data(self, form, **kwargs):
        context = super(EmissaoWizardView, self).get_context_data(form, **kwargs)
        context.update({
            'voucher': self.get_voucher(),
            'emissao': self.instance,
        })
        if self.steps.current == 'tela-confirmacao':
            context['dados_form1'] = self.get_cleaned_data_for_step('tela-1'),
            if 'tela-2' in self.templates:
                context['dados_form2'] = self.get_cleaned_data_for_step('tela-2')
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

    def save(self, form_list, **kwargs):
        emissao = self.instance
        emissao.requestor_user_id = self.request.user.pk
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

    def atualiza_voucher(self, voucher, form_step='tela-1'):
        dados_voucher = self.get_cleaned_data_for_step(form_step)

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
        'tela-1': 'certificados/nv1/wizard_tela_1.html',
        'tela-2': 'certificados/nv1/wizard_tela_2.html',
        'tela-confirmacao': 'certificados/nv1/wizard_tela_3_confirmacao.html'
    }


class EmissaoNv2WizardView(EmissaoWizardView):
    produtos_voucher = (Voucher.PRODUTO_SAN_UCC, Voucher.PRODUTO_MDC)
    templates = {
        'tela-1': 'certificados/nv2/wizard_tela_1.html',
        'tela-2': 'certificados/nv2/wizard_tela_2.html',
        'tela-confirmacao': 'certificados/nv2/wizard_tela_3_confirmacao.html'
    }


class EmissaoNv3WizardView(EmissaoWizardView):
    produtos_voucher = (Voucher.PRODUTO_EV,)
    templates = {
        'tela-1': 'certificados/nv3/wizard_tela_1.html',
        'tela-2': 'certificados/nv3/wizard_tela_2.html',
        'tela-confirmacao': 'certificados/nv3/wizard_tela_3_confirmacao.html'
    }


class EmissaoNv4WizardView(EmissaoWizardView):
    produtos_voucher = (Voucher.PRODUTO_EV_MDC,)
    templates = {
        'tela-1': 'certificados/nv4/wizard_tela_1.html',
        'tela-2': 'certificados/nv4/wizard_tela_2.html',
        'tela-confirmacao': 'certificados/nv4/wizard_tela_3_confirmacao.html'
    }


class EmissaoNvAWizardView(EmissaoWizardView):
    produtos_voucher = (Voucher.PRODUTO_JRE, Voucher.PRODUTO_CODE_SIGNING)
    templates = {
        'tela-1': 'certificados/nvA/wizard_tela_1.html',
        'tela-confirmacao': 'certificados/nvA/wizard_tela_2_confirmacao.html'
    }


class EmissaoNvBWizardView(EmissaoWizardView):
    produtos_voucher = (Voucher.PRODUTO_SMIME,)
    templates = {
        'tela-1': 'certificados/nvB/wizard_tela_1.html',
        'tela-confirmacao': 'certificados/nvB/wizard_tela_2_confirmacao.html'
    }