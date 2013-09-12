# coding=utf-8
from django.forms import ModelForm, CharField, EmailField
from portal.certificados.models import Emissao, Voucher
from portal.certificados.validations import ValidateCRMHashMixin
from portal.ferramentas.utils import get_razao_social_dominio, comparacao_fuzzy


class EmissaoModelForm(ModelForm, ValidateCRMHashMixin):
    user = None
    REQUIRED_FIELDS = ()

    class Meta:
        model = Emissao

    def __init__(self, user=None, **kwargs):
        self.user = user
        super(EmissaoModelForm, self).__init__(**kwargs)

        for f in self.REQUIRED_FIELDS:
            self.fields[f].required = True


class EmissaoNv0Tela1Form(EmissaoModelForm):

    class Meta(EmissaoModelForm.Meta):
        fields = ['emissao_url']


class EmissaoNv0Tela2Form(EmissaoModelForm):

    class Meta(EmissaoModelForm.Meta):
        fields = ['emissao_carta']


def show_nv0_tela2_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('tela-1') or {}
    try:
        voucher = Voucher.objects.get(crm_hash=cleaned_data.get('crm_hash'))
    except Voucher.DoesNotExist:
        # se o hash não existir o processamento não deve continuar, mas não é papel dessa função validar isso,
        # isso deve ser validado no clean_crm_hash
        return False

    if voucher.ssl_produto == voucher.PRODUTO_SITE_SEGURO:
        # validação do site seguro ocorre pela troca do DNS, então não precisa de carta de cessão
        return False

    razao_social = get_razao_social_dominio(cleaned_data.get('url'))
    return not (razao_social and comparacao_fuzzy(razao_social, voucher.cliente_razaosocial))


class EmissaoCallbackForm(ModelForm):
    callback_nome = CharField()
    callback_email = EmailField()
    callback_telefone = CharField()
    callback_observacao = CharField()


class EmissaoNv1Tela1Form(EmissaoModelForm, EmissaoCallbackForm):

    REQUIRED_FIELDS = ('emissao_url', 'emissao_csr')

    class Meta(EmissaoModelForm.Meta):
        fields = ['emissao_url', 'emissao_csr']


class EmissaoNv1Tela2Form(EmissaoModelForm):

    class Meta(EmissaoModelForm.Meta):
        fields = ['emissao_carta', 'emissao_validacao_email', 'emissao_certificado_envio_email',
                  'emissao_servidor_tipo']