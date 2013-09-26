# coding=utf-8
from django.forms import ModelForm, CharField, EmailField, PasswordInput, HiddenInput, ChoiceField, RadioSelect, Form
from portal.certificados.comodo import get_emails_validacao
from portal.certificados.models import Emissao, Voucher, Revogacao
from portal.certificados.validations import ValidateEmissaoCSRMixin, ValidateEmissaoValidacaoEmail, ValidateEmissaoValidacaoEmailMultiplo
from portal.ferramentas.utils import decode_csr, verifica_razaosocial_dominio, compare_csr
from django.core.exceptions import ValidationError


class EmissaoModelForm(ModelForm):
    user = None
    _crm_hash = None
    _voucher = None
    _csr_decoded = None
    _precisa_carta_cessao = None
    ValidationError = ValidationError
    REQUIRED_FIELDS = ()
    validacao_manual = False

    class Meta:
        model = Emissao

    def __init__(self, user=None, crm_hash=None, voucher=None, **kwargs):
        self.user = user
        self._crm_hash = crm_hash
        self._voucher = voucher
        super(EmissaoModelForm, self).__init__(**kwargs)

        for f in self.REQUIRED_FIELDS:
            self.fields[f].required = True
        if self.precisa_carta_cessao():
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

    def precisa_carta_cessao(self):
        if self._precisa_carta_cessao is None:
            dominio = self.initial.get('emission_url')
            if dominio:
                voucher = self.get_voucher()
                self._precisa_carta_cessao = not verifica_razaosocial_dominio(
                    voucher.customer_companyname,
                    dominio
                )
            else:
                self._precisa_carta_cessao = False

        return self._precisa_carta_cessao


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

    def clean(self):
        cleaned_data = super(EmissaoCallbackForm, self).clean()
        password = cleaned_data['callback_password']
        password2 = cleaned_data['callback_password_validacao']
        if password != password2:
            raise ValidationError('As senhas não são iguais')
        return cleaned_data


class EmissaoTela1Form(EmissaoModelForm, EmissaoCallbackForm, ValidateEmissaoCSRMixin):

    REQUIRED_FIELDS = ('emission_url', 'emission_csr')

    class Meta(EmissaoModelForm.Meta):
        fields = ['emission_url', 'emission_csr']


class EmissaoTela2MultiplosDominios(EmissaoModelForm, ValidateEmissaoCSRMixin, ValidateEmissaoValidacaoEmailMultiplo):
    _fqdns = None

    def get_domains_csr(self):
        if not self._fqdns:
            csr = self.get_csr_decoded(self.initial['emission_csr'])
            self._fqdns = csr.get('dnsNames', [])
        return self._fqdns

    def __init__(self, **kwargs):
        self.initial = kwargs.get('initial', {})
        kwargs.setdefault('initial', {})['emission_dcv_emails'] = ' ' * (len(self.get_domains_csr()) - 1)
        super(EmissaoTela2MultiplosDominios, self).__init__(**kwargs)


class EmissaoNv1Tela1Form(EmissaoTela1Form):
    pass


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

    def __init__(self, **kwargs):
        super(EmissaoNv1Tela2Form, self).__init__(**kwargs)
        choices_email = [(email, email) for email in get_emails_validacao(self.initial['emission_url'])]
        self.fields['emission_dcv_email'] = ChoiceField(choices=choices_email, widget=RadioSelect)


class EmissaoNv2Tela1Form(EmissaoTela1Form):
    pass


class EmissaoNv2Tela2Form(EmissaoTela2MultiplosDominios):

    REQUIRED_FIELDS = ('emission_url', 'emission_csr', 'emission_dcv_emails', 'emission_publickey_sendto',
                       'emission_server_type', 'emission_primary_dn')

    class Meta(EmissaoModelForm.Meta):
        fields = ['emission_url', 'emission_csr', 'emission_assignment_letter', 'emission_dcv_emails',
                  'emission_publickey_sendto', 'emission_server_type', 'emission_primary_dn']
        widgets = {
            'emission_url': HiddenInput,
            'emission_csr': HiddenInput,
            'emission_dcv_emails': HiddenInput,
        }


class EmissaoNv3Tela1Form(EmissaoTela1Form):
    validacao_manual = True


class EmissaoNv3Tela2Form(EmissaoModelForm, ValidateEmissaoCSRMixin, ValidateEmissaoValidacaoEmail):

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
        self.fields['emission_dcv_email'] = ChoiceField(choices=choices_email, widget=RadioSelect)


class EmissaoNv4Tela1Form(EmissaoTela1Form):
    validacao_manual = True


class EmissaoNv4Tela2Form(EmissaoTela2MultiplosDominios):

    validacao_manual = True

    REQUIRED_FIELDS = ('emission_url', 'emission_csr', 'emission_dcv_emails', 'emission_publickey_sendto',
                       'emission_server_type', 'emission_primary_dn', 'emission_articles_of_incorporation',
                       'emission_address_proof', 'emission_ccsa', 'emission_evcr')

    class Meta(EmissaoModelForm.Meta):
        fields = ['emission_url', 'emission_csr', 'emission_assignment_letter', 'emission_dcv_emails',
                  'emission_publickey_sendto', 'emission_server_type', 'emission_primary_dn',
                  'emission_articles_of_incorporation', 'emission_address_proof', 'emission_ccsa', 'emission_evcr']
        widgets = {
            'emission_url': HiddenInput,
            'emission_csr': HiddenInput,
            'emission_dcv_emails': HiddenInput,
        }


class EmissaoNvATela1Form(EmissaoModelForm, EmissaoCallbackForm):
    validacao_manual = True

    REQUIRED_FIELDS = ('emission_address_proof',)

    class Meta:
        fields = ['emission_address_proof']


class EmissaoNvBTela1Form(EmissaoModelForm, EmissaoCallbackForm):
    validacao_manual = True

    REQUIRED_FIELDS = ('emission_id', 'callback_tratamento', 'callback_nome', 'callback_sobrenome', 'callback_email',
                       'callback_telefone', 'callback_username', 'callback_password', 'callback_password_validacao')

    class Meta:
        fields = ['emission_id']


class EmissaoConfirmacaoForm(Form):

    confirma = CharField(widget=HiddenInput, initial='1')

    def clean_confirma(self):
        value = self.cleaned_data['confirma']
        if value != '1':
            raise self.ValidationError('Você precisa confirmar os dados')
        return value


class RevogacaoForm(ModelForm):

    class Meta:
        model = Revogacao
        fields = ('revoke_reason',)


class ReemissaoForm(EmissaoModelForm, EmissaoCallbackForm):
    validacao_manual = True

    class Meta:
        model = Emissao
        fields = ['emission_csr', 'emission_publickey_sendto']

    def clean_emission_csr(self):
        csr_nova = self.cleaned_data['emission_csr']
        csr_antiga = Emissao.objects.get(pk=self.instance.pk).emission_csr

        if not compare_csr(decode_csr(csr_nova), decode_csr(csr_antiga)):
            raise ValidationError('Único campo que pode mudar na CSR de reemissão é a chave pública')

        return csr_nova