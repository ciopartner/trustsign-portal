# coding=utf-8
from django.contrib.formtools.wizard.views import SessionWizardView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.renderers import UnicodeJSONRenderer, BrowsableAPIRenderer
from portal.certificados.authentication import UserPasswordAuthentication
from portal.certificados.forms import EmissaoNv0Tela1Form, EmissaoNv0Tela2Form, show_nv0_tela2_condition
from portal.certificados.models import Emissao
from portal.certificados.serializers import EmissaoNv0Serializer, EmissaoNv1Serializer, EmissaoNv2Serializer, \
    EmissaoNv3Serializer, EmissaoNv4Serializer, EmissaoNvASerializer


class EmissaoBaseList(ListModelMixin,
                      CreateModelMixin,
                      GenericAPIView):
    queryset = Emissao.objects.all()
    authentication_classes = [UserPasswordAuthentication]
    renderer_classes = [UnicodeJSONRenderer, BrowsableAPIRenderer]

    def get_serializer_context(self):
        """
        Coloca o usuário no kwargs do init do EmissaoSerializer
        """
        context = super(EmissaoBaseList, self).get_serializer_context()
        context.update({
            'user': self.request.user
        })
        return context

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class EmissaoNv0List(EmissaoBaseList):
    serializer_class = EmissaoNv0Serializer


class EmissaoNv1List(EmissaoBaseList):
    serializer_class = EmissaoNv1Serializer


class EmissaoNv2List(EmissaoBaseList):
    serializer_class = EmissaoNv2Serializer


class EmissaoNv3List(EmissaoBaseList):
    serializer_class = EmissaoNv3Serializer


class EmissaoNv4List(EmissaoBaseList):
    serializer_class = EmissaoNv4Serializer


class EmissaoNvAList(EmissaoBaseList):
    serializer_class = EmissaoNvASerializer


class ModelWithUserWizardView(SessionWizardView):
    model = None
    done_redirect_url = ''

    def dispatch(self, request, *args, **kwargs):
        self.instance = self.model()
        return super(ModelWithUserWizardView, self).dispatch(request, *args, **kwargs)

    def get_form_instance(self, step):
        return self.instance

    def done(self, form_list, **kwargs):
        self.instance.save()
        return HttpResponseRedirect(reverse(self.done_redirect_url))

    def get_form_kwargs(self, step=None):
        kwargs = super(ModelWithUserWizardView, self).get_form_kwargs(self, step)
        kwargs['user'] = self.request.user
        return kwargs


class EmissaoNv0WizardView(ModelWithUserWizardView):
    model = Emissao
    redirect_url_done = '/emissao-certificado-finalizada/'
    form_list = [('tela-1', EmissaoNv0Tela1Form), ('tela-2', EmissaoNv0Tela2Form)]
    condition_dict = {
        'tela-2': show_nv0_tela2_condition
    }