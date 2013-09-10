# coding=utf-8
from __future__ import unicode_literals
from django.core.exceptions import ValidationError as ValidationErrorDjango
from rest_framework.serializers import ModelSerializer, Serializer, ValidationError as ValidationErrorRest
from portal.certificados.comodo import get_emails_validacao
from portal.certificados.models import Voucher
from portal.ferramentas.utils import decode_csr, comparacao_fuzzy, get_razao_social_dominio


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
            attrs[source] = funcao_valida_campo(attrs[source], attrs)
            return attrs

        def clean_django(self):
            funcao_valida_campo = getattr(self, '_valida_%s' % field)
            return funcao_valida_campo(self.cleaned_data[field], self.cleaned_data)

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


@insere_metodos_validacao('crm_hash')
class ValidateCRMHashMixin(AddExcecaoMixin):

    def _valida_crm_hash(self, valor, fields):
        voucher = self.get_voucher(valor)
        if voucher.solicitante_user != self.user and not self.user.is_superuser:
            raise self.ValidationError('Este certificado não pertence à você')
        return valor


@insere_metodos_validacao('emissao_url')
class ValidateEmissaoUrlMixin(AddExcecaoMixin):

    def _valida_emissao_url(self, valor, fields):
        razao_social = get_razao_social_dominio(valor)
        if not razao_social:
            raise self.ValidationError('Não foi possível conseguir a razão social apartir da url informada')

        try:
            voucher = self.get_voucher()
        except Voucher.DoesNotExist:
            raise self.ValidationError('Voucher não encontrado')

        if not comparacao_fuzzy(razao_social, voucher.cliente_razaosocial):
            if fields.get('emissao_carta'):
                # se a razão social for diferente, mas o cliente enviar uma carta de cessão,
                # será preciso validação manual
                self.validacao_manual = True
            else:
                raise self.ValidationError('A entidade no registro.br não é a mesma da razão social do CNPJ.')
        return valor


@insere_metodos_validacao('emissao_csr')
class ValidateEmissaoCSRMixin(AddExcecaoMixin):

    def _valida_emissao_csr(self, valor, fields):
        try:
            voucher = self.get_voucher()
        except Voucher.DoesNotExist:
            raise self.ValidationError('Voucher não encontrado.')

        csr = self.get_csr_decoded(valor)

        if csr.get('CN') != voucher.ssl_url:
            raise self.ValidationError('O campo Common Name(CN) deve conter o domínio: %s' % voucher.ssl_url)

        if not comparacao_fuzzy(csr.get('O'), voucher.cliente_razaosocial):
            raise self.ValidationError('O campo Organization (O) deve conter a razão social: %s' % voucher.cliente_razaosocial)

        email = fields.get('emissao_validacao_email')
        if email and csr.get('Email') != email:
            raise self.ValidationError('O campo E-mail (Email) deve conter o e-mail: %s' % email)

        key_size = int(csr.get('KeySize'))
        if voucher.ssl_linha in (voucher.LINHA_BASIC, voucher.LINHA_PRO) and key_size != 2048:
            raise self.ValidationError('O tamanho da chave para produtos das linhas Basic e Pro deve ser 2048')

        if voucher.ssl_linha == voucher.LINHA_PRIME and key_size != 4096:
            raise self.ValidationError('O tamanho da chave para produtos da linha Prime deve ser 4096')

        if voucher.ssl_produto in (voucher.PRODUTO_MDC, voucher.PRODUTO_SAN_UCC, voucher.PRODUTO_EV_MDC):
            dominios = csr.get('dnsNames', [])
            if len(dominios) > voucher.ssl_dominios_qtde:
                raise self.ValidationError('A CSR possui mais domínios que a quantidade comprada: %s' % voucher.ssl_dominios_qtde)
            for dominio in dominios:
                razao_social = get_razao_social_dominio(dominio)
                if not razao_social:
                    raise self.ValidationError('Não foi possível conseguir a razão social apartir do domínio: %s' % dominio)
                if not comparacao_fuzzy(razao_social, voucher.cliente_razaosocial):
                    if fields.get('emissao_carta'):
                        self.validacao_manual = True
                    else:
                        raise Exception('A razão social do seu CNPJ não bate com a do domínio: %s' % dominio)
                #TODO: TBD > Chamar o serviço da COMODO de e-mails válidos para validar o e-mail de confirmação enviado pela API
        return valor


@insere_metodos_validacao('emissao_primary_dn')
class ValidateEmissaoPrimaryDN(AddExcecaoMixin):

    def _valida_emissao_primary_dn(self, valor, fields):
        csr = self.get_csr_decoded(fields['emissao_csr'])
        if not valor.strip() in csr.get('dnsNames'):
            raise self.ValidationError('O domínio primário não consta na lista de domínios na CSR')
        return valor


@insere_metodos_validacao('emissao_validacao_email')
class ValidateEmissaoValidacaoEmail(AddExcecaoMixin):

    def _valida_emissao_validacao_email(self, valor, fields):
        emails = get_emails_validacao(fields['emissao_url'])
        if valor not in emails:
            raise self.ValidationError('E-mail de validação inválido')
        return valor


@insere_metodos_validacao('emissao_contrato_social')
class ValidateEmissaoContratoSocial(AddExcecaoMixin):
    def _valida_emissao_contrato_social(self, valor, fields):
        #TODO: TBD > como vai funcionar o envio de arquivos pela API
        return valor


@insere_metodos_validacao('emissao_comprovante_endereco')
class ValidateEmissaoComprovanteEndereco(AddExcecaoMixin):
    def _valida_emissao_comprovante_endereco(self, valor, fields):
        #TODO: TBD > como vai funcionar o envio de arquivos pela API
        return valor


@insere_metodos_validacao('emissao_evcr')
class ValidateEmissaoEVCR(AddExcecaoMixin):
    def _valida_emissao_evcr(self, valor, fields):
        #TODO: TBD > como vai funcionar o envio de arquivos pela API
        return valor


@insere_metodos_validacao('emissao_ccsa')
class ValidateEmissaoCCSA(AddExcecaoMixin):
    def _valida_emissao_ccsa(self, valor, fields):
        #TODO: TBD > como vai funcionar o envio de arquivos pela API
        return valor


class EmissaoModelSerializer(ModelSerializer):
    REQUIRED_FIELDS = ()
    validacao_manual = False
    _csr_decoded = None
    _voucher = None
    user = None

    def __init__(self, user=None, **kwargs):
        self.user = user
        super(EmissaoModelSerializer, self).__init__(**kwargs)

    def get_csr_decoded(self, valor):
        if self._csr_decoded:
            csr = self._csr_decoded
        else:
            csr = decode_csr(valor)
            self._csr_decoded = csr
        return csr

    def get_fields(self):
        fields = super(EmissaoModelSerializer, self).get_fields()
        for f in self.REQUIRED_FIELDS:
            fields[f].required = True
        return fields

    def get_voucher(self, crm_hash):
        if not self._voucher:
            self._voucher = Voucher.objects.get(crm_hash=crm_hash)
        return self._voucher