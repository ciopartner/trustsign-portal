from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.renderers import UnicodeJSONRenderer, BrowsableAPIRenderer
from portal.certificados.authentication import UserPasswordAuthentication
from portal.certificados.models import Emissao
from portal.certificados.serializers import EmissaoNv0Serializer, EmissaoNv1Serializer, EmissaoNv2Serializer, \
    EmissaoNv3Serializer, EmissaoNv4Serializer, EmissaoNvASerializer


class EmissaoBaseList(ListModelMixin,
                      CreateModelMixin,
                      GenericAPIView):
    queryset = Emissao.objects.all()
    authentication_classes = [UserPasswordAuthentication]
    renderer_classes = [UnicodeJSONRenderer, BrowsableAPIRenderer]

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