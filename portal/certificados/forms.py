# coding=utf-8
from django.forms import ModelForm, HiddenInput
from portal.certificados.models import Emissao, Voucher
from portal.certificados.validations import ValidateCRMHashMixin
from portal.ferramentas.utils import get_razao_social_dominio, comparacao_fuzzy


class EmissaoModelForm(ModelForm, ValidateCRMHashMixin):
    user = None

    class Meta:
        model = Emissao
        fields = ['crm_hash']
        widgets = {
            'crm_hash': HiddenInput()
        }

    def __init__(self, user=None, **kwargs):
        self.user = user
        super(EmissaoModelForm, self).__init__(**kwargs)


class EmissaoNv0Tela1Form(EmissaoModelForm):

    class Meta(EmissaoModelForm.Meta):
        fields = ['crm_hash', 'emissao_url']


class EmissaoNv0Tela2Form(EmissaoModelForm):

    class Meta(EmissaoModelForm.Meta):
        fields = ['crm_hash', 'emissao_carta']


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