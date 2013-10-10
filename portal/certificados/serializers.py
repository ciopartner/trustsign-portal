# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework.fields import DateTimeField, CharField
from rest_framework.serializers import ModelSerializer, ValidationError
from portal.certificados.models import Emissao, Voucher, Revogacao
from portal.certificados.validations import ValidateEmissaoUrlMixin, ValidateEmissaoCSRMixin, \
    ValidateEmissaoValidacaoEmail, ValidateEmissaoValidacaoEmailMultiplo
from portal.ferramentas.utils import decode_csr, compare_csr, verifica_razaosocial_dominio


class VoucherSerializer(ModelSerializer):
    order_date = DateTimeField(format='%d/%m/%Y %H:%M', input_formats=['%d/%m/%Y', '%d/%m/%Y %H:%M'])

    class Meta:
        model = Voucher
        fields = ['crm_hash', 'customer_cnpj', 'customer_companyname', 'customer_zip', 'customer_address1',
                  'customer_address2', 'customer_address3', 'customer_address4', 'customer_city', 'customer_state',
                  'customer_country', 'customer_registration_status', 'customer_callback_firstname',
                  'customer_callback_lastname', 'customer_callback_email', 'customer_callback_phone',
                  'customer_callback_note', 'customer_callback_title', 'ssl_code', 'ssl_product', 'ssl_line',
                  'ssl_term', 'ssl_key_size', 'ssl_username', 'ssl_password', 'order_date', 'order_item_value',
                  'order_channel', 'order_number']

    def validate_crm_hash(self, attrs, source):
        crm_hash = attrs.get(source)
        if Voucher.objects.filter(crm_hash=crm_hash).exists():
            raise ValidationError('CRM Hash já existente!')
        return attrs


class RevogacaoSerializer(ModelSerializer):

    order_date = DateTimeField(format='%d/%m/%Y %H:%M')

    class Meta:
        model = Revogacao
        fields = ['crm_hash', 'revoke_reason']


class ReemissaoSerializer(ModelSerializer):

    class Meta:
        model = Emissao
        fields = ['crm_hash', 'emission_csr']

    def validate_emission_csr(self, attrs, source):
        csr_nova = attrs.get(source)
        csr_antiga = Emissao.objects.get(pk=self.object.pk).emission_csr

        if not compare_csr(decode_csr(csr_nova), decode_csr(csr_antiga)):
            raise ValidationError('Único campo que pode mudar na CSR de reemissão é a chave pública')

        return attrs


class EmissaoModelSerializer(ModelSerializer):
    REQUIRED_FIELDS = ()
    validacao_manual = False
    _csr_decoded = None
    _voucher = None
    user = None
    ValidationError = ValidationError
    validacao = False
    _precisa_carta_cessao = None

    def __init__(self, user=None, crm_hash=None, **kwargs):
        self.user = user
        self._crm_hash = crm_hash
        super(EmissaoModelSerializer, self).__init__(**kwargs)

    def get_csr_decoded(self, valor):
        if not self._csr_decoded:
            self._csr_decoded = decode_csr(valor)
        return self._csr_decoded

    def get_fields(self):
        fields = super(EmissaoModelSerializer, self).get_fields()
        for f in self.get_required_fields():
            if f in fields:
                fields[f].required = True
        return fields

    def get_voucher(self):
        if not self._voucher:
            self._voucher = Voucher.objects.get(crm_hash=self._crm_hash)
        return self._voucher

    def get_required_fields(self):
        if self.precisa_carta_cessao():
            return self.REQUIRED_FIELDS + ('emission_assignment_letter',)
        return self.REQUIRED_FIELDS

    def precisa_carta_cessao(self):
        if self._precisa_carta_cessao is None:
            dominio = self.init_data.get('emission_url')
            if dominio:
                voucher = self.get_voucher()
                self._precisa_carta_cessao = not verifica_razaosocial_dominio(
                    voucher.customer_companyname,
                    dominio
                )
            else:
                self._precisa_carta_cessao = False

        return self._precisa_carta_cessao


class EmissaoNv0Serializer(EmissaoModelSerializer, ValidateEmissaoUrlMixin):
    REQUIRED_FIELDS = ('emission_url', )

    class Meta:
        model = Emissao
        fields = ('crm_hash', 'emission_url', 'emission_assignment_letter')


class EmissaoNv1Serializer(EmissaoModelSerializer, ValidateEmissaoUrlMixin, ValidateEmissaoCSRMixin, ValidateEmissaoValidacaoEmail):
    REQUIRED_FIELDS = ('emission_url', 'emission_dcv_emails', 'emission_publickey_sendto',
                       'emission_server_type', 'emission_csr')

    class Meta:
        model = Emissao
        fields = ('crm_hash', 'emission_url', 'emission_dcv_emails', 'emission_publickey_sendto',
                  'emission_server_type', 'emission_csr', 'emission_assignment_letter')


class EmissaoNv2Serializer(EmissaoModelSerializer, ValidateEmissaoUrlMixin, ValidateEmissaoCSRMixin, ValidateEmissaoValidacaoEmailMultiplo):
    REQUIRED_FIELDS = ('emission_dcv_emails', 'emission_publickey_sendto', 'emission_server_type', 'emission_csr',)

    class Meta:
        model = Emissao
        fields = ('crm_hash', 'emission_url', 'emission_csr', 'emission_dcv_emails',
                  'emission_publickey_sendto', 'emission_server_type', 'emission_assignment_letter')


class EmissaoNv3Serializer(EmissaoModelSerializer, ValidateEmissaoUrlMixin, ValidateEmissaoCSRMixin, ValidateEmissaoValidacaoEmail):
    validacao_manual = True

    REQUIRED_FIELDS = ('emission_url', 'emission_dcv_emails', 'emission_publickey_sendto',
                       'emission_server_type', 'emission_csr', 'emission_articles_of_incorporation',
                       'emission_address_proof', 'emission_ccsa', 'emission_evcr')

    class Meta:
        model = Emissao
        fields = ('crm_hash', 'emission_url', 'emission_publickey_sendto', 'emission_dcv_emails',
                  'emission_server_type', 'emission_csr', 'emission_assignment_letter',
                  'emission_articles_of_incorporation', 'emission_address_proof', 'emission_ccsa', 'emission_evcr')


class EmissaoNv4Serializer(EmissaoModelSerializer, ValidateEmissaoUrlMixin, ValidateEmissaoCSRMixin, ValidateEmissaoValidacaoEmailMultiplo):
    REQUIRED_FIELDS = ('emission_dcv_emails', 'emission_publickey_sendto',
                       'emission_server_type', 'emission_csr', 'emission_articles_of_incorporation',
                       'emission_address_proof', 'emission_ccsa', 'emission_evcr')

    class Meta:
        model = Emissao
        fields = ('crm_hash', 'emission_url', 'emission_fqdns', 'emission_publickey_sendto',
                  'emission_dcv_emails', 'emission_server_type', 'emission_csr',
                  'emission_assignment_letter', 'emission_articles_of_incorporation', 'emission_address_proof',
                  'emission_ccsa', 'emission_evcr')


class EmissaoNvASerializer(EmissaoModelSerializer):
    REQUIRED_FIELDS = ('emission_csr', 'emission_phone_proof')

    class Meta:
        model = Emissao
        fields = ('crm_hash', 'emission_csr', 'emission_address_proof', 'emission_phone_proof')


class EmissaoNvBSerializer(EmissaoModelSerializer):
    REQUIRED_FIELDS = ('emission_id', 'emission_revoke_password')

    emission_revoke_password2 = CharField(max_length=128)

    class Meta:
        model = Emissao
        fields = ('crm_hash', 'emission_id', 'emission_revoke_password')


class EmissaoValidaSerializer(EmissaoModelSerializer, ValidateEmissaoUrlMixin, ValidateEmissaoCSRMixin):
    REQUIRED_FIELDS = ('emission_url', 'emission_csr', )
    validacao = True
    validacao_carta_cessao_necessaria = False

    class Meta:
        model = Emissao
        fields = ('crm_hash', 'emission_url', 'emission_csr')