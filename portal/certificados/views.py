# coding=utf-8
import os
from django.contrib.formtools.wizard.views import SessionWizardView
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.renderers import UnicodeJSONRenderer, BrowsableAPIRenderer
from portal.certificados.authentication import UserPasswordAuthentication
from portal.certificados.models import Emissao, Voucher
from portal.certificados.serializers import EmissaoNv0Serializer, EmissaoNv1Serializer, EmissaoNv2Serializer, \
    EmissaoNv3Serializer, EmissaoNv4Serializer, EmissaoNvASerializer
from django.conf import settings


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
        if voucher.ssl_produto in (voucher.PRODUTO_SITE_SEGURO, voucher.PRODUTO_SITE_MONITORADO):
            return EmissaoNv0Serializer
        if voucher.ssl_produto in (voucher.PRODUTO_SSL, voucher.PRODUTO_SSL_WILDCARD):
            return EmissaoNv1Serializer
        if voucher.ssl_produto in (voucher.PRODUTO_SAN_UCC, voucher.PRODUTO_MDC):
            return EmissaoNv2Serializer
        if voucher.ssl_produto == voucher.PRODUTO_EV:
            return EmissaoNv3Serializer
        if voucher.ssl_produto == voucher.PRODUTO_EV_MDC:
            return EmissaoNv4Serializer
        if voucher.ssl_produto in (voucher.PRODUTO_JRE, voucher.PRODUTO_CODE_SIGNING, voucher.PRODUTO_SMIME):
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


class ModelWithUserWizardView(SessionWizardView):
    model = None
    done_redirect_url = ''
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'forms'))
    template_name = 'base.html'

    def dispatch(self, request, *args, **kwargs):
        self.instance = self.model()
        return super(ModelWithUserWizardView, self).dispatch(request, *args, **kwargs)

    def get_form_instance(self, step):
        return self.instance

    def done(self, form_list, **kwargs):
        self.instance.save()
        return HttpResponseRedirect(reverse(self.done_redirect_url))

    def get_form_kwargs(self, step=None):
        kwargs = super(ModelWithUserWizardView, self).get_form_kwargs(step)
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, form, **kwargs):
        context = super(ModelWithUserWizardView, self).get_context_data(form, **kwargs)
        try:
            context.update({
                'voucher': Voucher.objects.get(crm_hash=self.kwargs['crm_hash'])
            })
        except Voucher.DoesNotExist:
            #raise Http404
            print 'nao encontrou'
        return context


class EmissaoNv1WizardView(ModelWithUserWizardView):
    model = Emissao
    redirect_url_done = '/emissao-certificado-finalizada/'

    def get_template_names(self):
        return ['certificados/form_nv1_1_ssl.html', 'certificados/form_nv1_2_ssl.html']