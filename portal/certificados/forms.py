# coding=utf-8
from django.forms import ModelForm, CharField, EmailField, PasswordInput, HiddenInput, ChoiceField, RadioSelect
from portal.certificados.comodo import get_emails_validacao
from portal.certificados.models import Emissao, Voucher
from portal.certificados.validations import ValidateEmissaoCSRMixin, ValidateEmissaoValidacaoEmail
from portal.ferramentas.utils import decode_csr
from django.core.exceptions import ValidationError


class EmissaoModelForm(ModelForm):
    user = None
    _crm_hash = None
    _voucher = None
    _csr_decoded = None
    ValidationError = ValidationError
    REQUIRED_FIELDS = ()

    class Meta:
        model = Emissao

    def __init__(self, user=None, crm_hash=None, voucher=None, precisa_carta_cessao=False, **kwargs):
        self.user = user
        self._crm_hash = crm_hash
        self._voucher = voucher
        super(EmissaoModelForm, self).__init__(**kwargs)

        for f in self.REQUIRED_FIELDS:
            self.fields[f].required = True
        if precisa_carta_cessao:
            f = self.fields.get('emission_assignment_letter')
            if f:
                f.required = True

    def get_voucher(self):
        if not self._voucher:
            self._voucher = Voucher.objects.get(crm_hash=self._crm_hash)
        return self._voucher

    def get_csr_decoded(self, valor):
        if not self._csr_decoded:
            self._csr_decoded = decode_csr(valor)
        return self._csr_decoded


class EmissaoCallbackForm(ModelForm):
    callback_tratamento = CharField(required=False)
    callback_nome = CharField()
    callback_sobrenome = CharField()
    callback_email = EmailField()
    callback_telefone = CharField()
    callback_observacao = CharField(required=False)
    callback_username = CharField(required=False)
    callback_password = CharField(widget=PasswordInput, required=False)
    callback_password_validacao = CharField(widget=PasswordInput, required=False)

    def clean_callback_telefone(self):
        valor = self.cleaned_data['callback_telefone']

        #TODO: Validar se é telefone fixo

        return valor


class EmissaoNv1Tela1Form(EmissaoModelForm, EmissaoCallbackForm, ValidateEmissaoCSRMixin):

    REQUIRED_FIELDS = ('emission_url', 'emission_csr')

    class Meta(EmissaoModelForm.Meta):
        fields = ['emission_url', 'emission_csr']


class EmissaoNv1Tela2Form(EmissaoModelForm, ValidateEmissaoCSRMixin, ValidateEmissaoValidacaoEmail):

    REQUIRED_FIELDS = ('emission_url', 'emission_csr', 'emission_dcv_emails', 'emission_publickey_sendto',
                       'emission_server_type')

    class Meta(EmissaoModelForm.Meta):
        fields = ['emission_url', 'emission_csr', 'emission_assignment_letter', 'emission_dcv_emails',
                  'emission_publickey_sendto', 'emission_server_type']
        widgets = {
            'emission_url': HiddenInput,
            'emission_csr': HiddenInput,
        }


class EmissaoNv2Tela1Form(EmissaoModelForm, EmissaoCallbackForm, ValidateEmissaoCSRMixin):

    REQUIRED_FIELDS = ('emission_url', 'emission_csr')

    class Meta(EmissaoModelForm.Meta):
        fields = ['emission_url', 'emission_csr']


class EmissaoNv2Tela2Form(EmissaoModelForm, ValidateEmissaoCSRMixin, ValidateEmissaoValidacaoEmail ):

    REQUIRED_FIELDS = ('emission_url', 'emission_csr', 'emission_dcv_emails', 'emission_publickey_sendto',
                       'emission_server_type')

    class Meta(EmissaoModelForm.Meta):
        fields = ['emission_url', 'emission_csr', 'emission_assignment_letter', 'emission_dcv_emails',
                  'emission_publickey_sendto', 'emission_server_type']
        widgets = {
            'emission_url': HiddenInput,
            'emission_csr': HiddenInput,
        }


class EmissaoNv3Tela1Form(EmissaoModelForm, EmissaoCallbackForm, ValidateEmissaoCSRMixin):

    REQUIRED_FIELDS = ('emission_url', 'emission_csr')

    class Meta(EmissaoModelForm.Meta):
        fields = ['emission_url', 'emission_csr']


class EmissaoNv3Tela2Form(EmissaoModelForm, ValidateEmissaoCSRMixin, ValidateEmissaoValidacaoEmail):

    REQUIRED_FIELDS = ('emission_url', 'emission_csr', 'emission_dcv_emails', 'emission_publickey_sendto',
                       'emission_server_type')

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
        self.fields['emission_dcv_email'] = ChoiceField(choices=choices_email, widget=RadioSelect)