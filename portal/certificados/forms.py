# coding=utf-8
from django.forms import ModelForm, CharField, EmailField, PasswordInput, HiddenInput
from portal.certificados.models import Emissao, Voucher
from portal.certificados.validations import ValidateCRMHashMixin, ValidateEmissaoCSRMixin, ValidateEmissaoValidacaoEmail
from portal.ferramentas.utils import get_razao_social_dominio, comparacao_fuzzy, decode_csr
from django.core.exceptions import ValidationError


class EmissaoModelForm(ModelForm, ValidateCRMHashMixin):
    user = None
    _crm_hash = None
    _voucher = None
    _csr_decoded = None
    ValidationError = ValidationError
    REQUIRED_FIELDS = ()

    class Meta:
        model = Emissao

    def __init__(self, user=None, crm_hash=None, precisa_carta_cessao=False, **kwargs):
        self.user = user
        self._crm_hash = crm_hash
        super(EmissaoModelForm, self).__init__(**kwargs)

        for f in self.REQUIRED_FIELDS:
            self.fields[f].required = True
        if precisa_carta_cessao:
            f = self.fields.get('emissao_carta')
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

    REQUIRED_FIELDS = ('emissao_url', 'emissao_csr')

    class Meta(EmissaoModelForm.Meta):
        fields = ['emissao_url', 'emissao_csr']

    def __init__(self, **kwargs):
        initial = kwargs.pop('initial', {})
        self._crm_hash = kwargs.get('crm_hash', None)
        voucher = self.get_voucher()
        initial.update({
            'callback_tratamento': voucher.cliente_callback_tratamento,
            'callback_nome': voucher.cliente_callback_nome,
            'callback_sobrenome': voucher.cliente_callback_sobrenome,
            'callback_email': voucher.cliente_callback_email,
            'callback_telefone': voucher.cliente_callback_telefone,
            'callback_observacao': voucher.cliente_callback_observacao,
            'callback_username': voucher.cliente_callback_username,
        })
        super(EmissaoNv1Tela1Form, self).__init__(initial=initial, **kwargs)


class EmissaoNv1Tela2Form(EmissaoModelForm, ValidateEmissaoCSRMixin, ValidateEmissaoValidacaoEmail ):

    REQUIRED_FIELDS = ('emissao_url', 'emissao_csr', 'emissao_validacao_email', 'emissao_certificado_envio_email', 'emissao_servidor_tipo')

    class Meta(EmissaoModelForm.Meta):
        fields = ['emissao_url', 'emissao_csr', 'emissao_carta', 'emissao_validacao_email', 'emissao_certificado_envio_email',
                  'emissao_servidor_tipo']
        widgets = {
            'emissao_url': HiddenInput,
            'emissao_csr': HiddenInput,
        }