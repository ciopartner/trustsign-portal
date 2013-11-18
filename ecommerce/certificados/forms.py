# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

from django.forms import ModelForm, CharField, EmailField, PasswordInput, HiddenInput, ChoiceField, RadioSelect, Form, TextInput
from django.core.exceptions import ValidationError
from passwords.fields import PasswordField
from ecommerce.certificados import erros as e
from ecommerce.certificados.erros import get_erro_message

from libs.comodo import get_emails_validacao
from ecommerce.certificados.models import Emissao, Voucher, Revogacao
from ecommerce.certificados.validations import ValidateEmissaoCSRMixin, ValidateEmissaoValidacaoEmail, \
    ValidateEmissaoValidacaoEmailMultiplo, ValidateEmissaoAssignmentLetter, ValidateEmissaoArticlesOfIncorporation, ValidateEmissaoAddressProof, ValidateEmissaoCCSA, ValidateEmissaoEVCR, ValidateEmissaoPhoneProof, ValidateEmissaoID, ValidateEmissaoUrlMixin
from portal.suporte.utils import decode_csr, verifica_razaosocial_dominio, compare_csr, comparacao_fuzzy


class EmissaoModelForm(ModelForm):
    user = None
    _crm_hash = None
    _voucher = None
    _csr_decoded = None
    _precisa_carta_cessao = None
    ValidationError = ValidationError
    REQUIRED_FIELDS = ()
    validacao_manual = False
    validacao = False

    class Meta:
        model = Emissao

    def __init__(self, user=None, crm_hash=None, voucher=None, **kwargs):
        self.user = user
        self._crm_hash = crm_hash
        self._voucher = voucher
        super(EmissaoModelForm, self).__init__(**kwargs)

        for f in self.REQUIRED_FIELDS:
            self.fields[f].required = True

        f = self.fields.get('emission_assignment_letter')
        if f and self.precisa_carta_cessao():
            f.required = True

    def get_voucher(self):
        if not self._voucher:
            self._voucher = Voucher.objects.get(crm_hash=self._crm_hash)
        return self._voucher

    def get_csr_decoded(self, valor):
        if not self._csr_decoded:
            self._csr_decoded = decode_csr(valor)
        return self._csr_decoded

    _fqdns = None

    def get_domains_csr(self):
        if not self._fqdns:
            csr = self.get_csr_decoded(self.initial['emission_csr'])
            self._fqdns = csr.get('dnsNames', [])
        return self._fqdns

    def precisa_carta_cessao(self):
        if self._precisa_carta_cessao is None:
            voucher = self.get_voucher()

            csr = self.get_csr_decoded(self.initial.get('emission_csr'))

            if not comparacao_fuzzy(csr.get('O'), voucher.customer_companyname):
                self._precisa_carta_cessao = True

            elif voucher.ssl_product in (Voucher.PRODUTO_CODE_SIGNING, Voucher.PRODUTO_JRE):
                self._precisa_carta_cessao = not comparacao_fuzzy(csr.get('CN'), voucher.customer_companyname)

            elif voucher.ssl_product in (Voucher.PRODUTO_MDC, Voucher.PRODUTO_EV_MDC):
                self._precisa_carta_cessao = any(not verifica_razaosocial_dominio(
                    voucher.customer_companyname,
                    dominio
                ) for dominio in self.get_domains_csr())

            else:
                dominio = self.initial.get('emission_url')

                if dominio:
                    self._precisa_carta_cessao = not verifica_razaosocial_dominio(
                        voucher.customer_companyname,
                        dominio
                    )
                else:
                    self._precisa_carta_cessao = False

                #SAN valida o emission_url e os dominios na CSR
                if not self._precisa_carta_cessao and voucher.ssl_product == Voucher.PRODUTO_SAN_UCC:
                    self._precisa_carta_cessao = any(not verifica_razaosocial_dominio(
                        voucher.customer_companyname,
                        dominio
                    ) for dominio in self.get_domains_csr())

            if self._precisa_carta_cessao:
                self.validacao_manual = True

        return self._precisa_carta_cessao


class EmissaoCallbackForm(ModelForm):
    callback_tratamento = CharField(required=False)
    callback_nome = CharField()
    callback_sobrenome = CharField()
    callback_email = EmailField()
    callback_telefone = CharField(widget=TextInput(attrs={'class': 'mask-phone'}))
    callback_observacao = CharField(required=False)
    callback_username = CharField(required=False, error_messages={})

    def clean_callback_telefone(self):
        self.clean()
        valor = self.cleaned_data['callback_telefone']

        if not re.match('\([0-9]{2}\) [0-9]{4}-[0-9]{4}', valor) or valor[5] not in '2345':
            raise ValidationError(e.get_erro_message(e.ERRO_DADOS_CONTATO_TELEFONE_PRECISA_SER_FIXO))

        return valor


class EmissaoTela1Form(EmissaoModelForm, ValidateEmissaoCSRMixin):

    REQUIRED_FIELDS = ('emission_url', 'emission_csr')

    class Meta(EmissaoModelForm.Meta):
        fields = ['emission_url', 'emission_csr']


class EmissaoTela2MultiplosDominios(EmissaoModelForm, EmissaoCallbackForm, ValidateEmissaoCSRMixin,
                                    ValidateEmissaoValidacaoEmailMultiplo):

    def __init__(self, **kwargs):
        self.initial = kwargs.get('initial', {})
        dominios = self.get_domains_csr()
        kwargs.setdefault('initial', {})['emission_dcv_emails'] = ' ' * (len(dominios) - 1)
        super(EmissaoTela2MultiplosDominios, self).__init__(**kwargs)

        url = self.initial['emission_url']

        if self.get_voucher().ssl_product == Voucher.PRODUTO_SAN_UCC and url not in dominios:
            dominios.insert(0, url)

    def get_dict_domains_email(self):
        d = {}
        for dominio in self.get_domains_csr():
            d[dominio] = get_emails_validacao(dominio)
        return d


class EmissaoNv1Tela1Form(EmissaoTela1Form):
    pass


class EmissaoNv1Tela2Form(EmissaoModelForm, EmissaoCallbackForm, ValidateEmissaoUrlMixin, ValidateEmissaoCSRMixin,
                          ValidateEmissaoValidacaoEmail, ValidateEmissaoAssignmentLetter):

    REQUIRED_FIELDS = ('emission_url', 'emission_csr', 'emission_dcv_emails', 'emission_publickey_sendto',
                       'emission_server_type')

    class Meta(EmissaoModelForm.Meta):
        fields = ['emission_url', 'emission_csr', 'emission_assignment_letter', 'emission_dcv_emails',
                  'emission_publickey_sendto', 'emission_server_type']
        widgets = {
            'emission_url': HiddenInput,
            'emission_csr': HiddenInput,
        }

    def __init__(self, **kwargs):
        super(EmissaoNv1Tela2Form, self).__init__(**kwargs)
        choices_email = [(email, email) for email in get_emails_validacao(self.initial['emission_url'])]
        self.fields['emission_dcv_emails'] = ChoiceField(choices=choices_email, widget=RadioSelect)


class EmissaoNv2Tela1Form(EmissaoTela1Form):

    def __init__(self, **kwargs):
        super(EmissaoNv2Tela1Form, self).__init__(**kwargs)
        voucher = self.get_voucher()

        if voucher.ssl_product == Voucher.PRODUTO_MDC:
            self.REQUIRED_FIELDS = ('emission_csr',)
            self.fields['emission_url'].required = False


class EmissaoNv2Tela2Form(EmissaoTela2MultiplosDominios, ValidateEmissaoUrlMixin, ValidateEmissaoAssignmentLetter):

    REQUIRED_FIELDS = ('emission_url', 'emission_csr', 'emission_dcv_emails', 'emission_publickey_sendto',
                       'emission_server_type')

    class Meta(EmissaoModelForm.Meta):
        fields = ['emission_url', 'emission_csr', 'emission_assignment_letter', 'emission_dcv_emails',
                  'emission_publickey_sendto', 'emission_server_type']
        widgets = {
            'emission_url': HiddenInput,
            'emission_csr': HiddenInput,
            'emission_dcv_emails': HiddenInput,
        }

    def __init__(self, **kwargs):
        super(EmissaoNv2Tela2Form, self).__init__(**kwargs)
        voucher = self.get_voucher()

        if voucher.ssl_product == Voucher.PRODUTO_MDC:
            self.REQUIRED_FIELDS = ('emission_csr', 'emission_dcv_emails', 'emission_publickey_sendto',
                                    'emission_server_type')
            self.fields['emission_url'].required = False


class EmissaoNv3Tela1Form(EmissaoTela1Form):
    validacao_manual = True


class EmissaoNv3Tela2Form(EmissaoModelForm, EmissaoCallbackForm, ValidateEmissaoUrlMixin, ValidateEmissaoCSRMixin,
                          ValidateEmissaoValidacaoEmail, ValidateEmissaoAssignmentLetter,
                          ValidateEmissaoArticlesOfIncorporation, ValidateEmissaoAddressProof, ValidateEmissaoCCSA,
                          ValidateEmissaoEVCR):

    REQUIRED_FIELDS = ('emission_url', 'emission_csr', 'emission_dcv_emails', 'emission_publickey_sendto',
                       'emission_server_type', 'emission_articles_of_incorporation', 'emission_address_proof',
                       'emission_ccsa', 'emission_evcr')
    validacao_manual = True

    class Meta(EmissaoModelForm.Meta):
        fields = ['emission_url', 'emission_csr', 'emission_assignment_letter', 'emission_dcv_emails',
                  'emission_publickey_sendto', 'emission_server_type', 'emission_articles_of_incorporation',
                  'emission_address_proof', 'emission_ccsa', 'emission_evcr']
        widgets = {
            'emission_url': HiddenInput,
            'emission_csr': HiddenInput,
        }

    def __init__(self, **kwargs):
        super(EmissaoNv3Tela2Form, self).__init__(**kwargs)
        choices_email = [(email, email) for email in get_emails_validacao(self.initial['emission_url'])]
        self.fields['emission_dcv_emails'] = ChoiceField(choices=choices_email, widget=RadioSelect)


class EmissaoNv4Tela1Form(EmissaoTela1Form):
    validacao_manual = True

    REQUIRED_FIELDS = ('emission_csr',)


class EmissaoNv4Tela2Form(EmissaoTela2MultiplosDominios, ValidateEmissaoAssignmentLetter,
                          ValidateEmissaoArticlesOfIncorporation, ValidateEmissaoAddressProof, ValidateEmissaoCCSA,
                          ValidateEmissaoEVCR):

    validacao_manual = True

    REQUIRED_FIELDS = ('emission_csr', 'emission_dcv_emails', 'emission_publickey_sendto', 'emission_server_type',
                       'emission_articles_of_incorporation', 'emission_address_proof', 'emission_ccsa', 'emission_evcr')

    class Meta(EmissaoModelForm.Meta):
        fields = ['emission_csr', 'emission_assignment_letter', 'emission_dcv_emails',
                  'emission_publickey_sendto', 'emission_server_type', 'emission_articles_of_incorporation',
                  'emission_address_proof', 'emission_ccsa', 'emission_evcr']
        widgets = {
            'emission_url': HiddenInput,
            'emission_csr': HiddenInput,
            'emission_dcv_emails': HiddenInput,
        }


class EmissaoNvATela1Form(EmissaoModelForm, EmissaoCallbackForm, ValidateEmissaoPhoneProof):
    validacao_manual = True

    REQUIRED_FIELDS = ('emission_csr', 'emission_phone_proof',)

    class Meta(EmissaoModelForm.Meta):
        fields = ['emission_csr', 'emission_phone_proof']


class EmissaoNvBTela1Form(EmissaoModelForm, EmissaoCallbackForm, ValidateEmissaoID):
    validacao_manual = True

    REQUIRED_FIELDS = ('emission_id', 'emission_revoke_password')

    emission_revoke_password = PasswordField()

    emission_revoke_password_confirmation = CharField(widget=PasswordInput)

    class Meta(EmissaoModelForm.Meta):
        fields = ('emission_id', 'emission_revoke_password')


class EmissaoConfirmacaoForm(Form):

    confirma = CharField(widget=HiddenInput, initial='1')
    validacao_manual = False

    def __init__(self, user=None, crm_hash=None, voucher=None, **kwargs):
        self.user = user
        self._crm_hash = crm_hash
        self._voucher = voucher
        super(EmissaoConfirmacaoForm, self).__init__(**kwargs)

    def clean_confirma(self):
        value = self.cleaned_data['confirma']
        if value != '1':
            raise ValidationError('Você precisa confirmar os dados')
        return value


class RevogacaoForm(ModelForm):

    emission_url = CharField(max_length=256, required=False)

    class Meta:
        model = Revogacao
        fields = ('revoke_reason',)

    def __init__(self, voucher=None, **kwargs):
        self.voucher = voucher
        super(RevogacaoForm, self).__init__(**kwargs)

    def clean_emission_url(self):
        emission_url = self.cleaned_data.get('emission_url')

        emissao = self.voucher.emissao
        if emission_url != emissao.emission_url:
            raise ValidationError(e.get_erro_message(e.ERRO_REVOGACAO_VALIDACAO_DOMINIO))

        return emission_url


class ReemissaoForm(EmissaoModelForm, EmissaoCallbackForm):
    validacao_manual = True

    class Meta:
        model = Emissao
        fields = ['emission_csr', 'emission_publickey_sendto']

    def clean_emission_csr(self):
        csr_nova = self.cleaned_data['emission_csr']
        csr_antiga = Emissao.objects.get(pk=self.instance.pk).emission_csr

        if not compare_csr(decode_csr(csr_nova), decode_csr(csr_antiga)):
            raise ValidationError(e.get_erro_message(e.ERRO_CSR_REEMISSAO_CHAVE_PUBLICA))

        return csr_nova