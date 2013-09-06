# coding=utf-8
import commands
import re
from django.core.exceptions import ValidationError as ValidationErrorDjango
from rest_framework.serializers import ModelSerializer, Serializer, ValidationError as ValidationErrorRest


def insere_metodos_validacao(field):
    """
    Decorator que cria os métodos clean_FIELD e validate_FIELD usados pelo
    form do django e pelo serializer do djangorestframework respectivamente,
    que por sua vez chama o método _valida_FIELD onde deve ser conter a validação

    Exemplo:
        @insere_metodos_validacao('campo')
        class ValidateCampoMixin(object):
            def _valida_campo(self, valor):
                ...
                return valor
    """
    def wrap(klass):
        def validade_rest(self, attrs, source):
            funcao_valida_campo = getattr(self, '_valida_%s' % field)
            attrs[source] = funcao_valida_campo(attrs[source])
            return attrs

        def clean_django(self):
            funcao_valida_campo = getattr(self, '_valida_%s' % field)
            return funcao_valida_campo(self.cleaned_data[field])

        setattr(klass, 'clean_%s' % field, clean_django)
        setattr(klass, 'validate_%s' % field, validade_rest)

        return klass
    return wrap


class AddExcecaoMixin(object):
    """
    Adiciona o ValidationError correto na classe, pois o django e o djangorestframework usam diferentes classes
    Deve ser usado: raise self.ValidationError
    """
    ValidationError = Exception
    cleaned_data = None

    def __init__(self, *args, **kwargs):
        super(AddExcecaoMixin, self).__init__(**kwargs)
        self.ValidationError = ValidationErrorRest if isinstance(self, Serializer) else ValidationErrorDjango


@insere_metodos_validacao('emissao_url')
class ValidateEmissaoUrlMixin(AddExcecaoMixin):

    def _valida_emissao_url(self, valor):
        razao_social = commands.getoutput('whois %s | grep ^owner:' % valor)
        r = re.match('owner:\s*(.+)', razao_social)
        if r:
            razao_social = r.groups()[0]
            dados = self.get_dados_empresa()  # TODO: dados da empresa estão no voucher, não precisa buscar no knu novamente
            if razao_social != dados['razao_social']:
                raise self.ValidationError('A entidade no registro.br não é a mesma da razão social do CNPJ.')
        return valor


@insere_metodos_validacao('emissao_csr')
class ValidateEmissaoCSRMixin(AddExcecaoMixin):

    def _valida_emissao_csr(self, valor):

        return valor


@insere_metodos_validacao('emissao_primary_dn')
class ValidateEmissaoPrimaryDN(object):

    def _valida_emissao_primary_dn(self, valor):

        return valor


class CustomModelSerializer(ModelSerializer):
    REQUIRED_FIELDS = ()

    def get_fields(self):
        fields = super(CustomModelSerializer, self).get_fields()
        for f in self.REQUIRED_FIELDS:
            fields[f].required = True
        return fields


