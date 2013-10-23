# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.forms import CharField, TextInput
from localflavor.br.forms import BRCNPJField
from oscar.apps.customer.forms import EmailUserCreationForm as CoreEmailUserCreationForm
from ecommerce.website.utils import get_dados_empresa

User = get_user_model()


class TextInputDisabled(TextInput):
    def __init__(self, *args, **kwargs):
        super(TextInputDisabled, self).__init__(*args, **kwargs)
        self.attrs['disabled'] = 'disabled'


class CharFieldDisabled(CharField):
    widget = TextInputDisabled

    def __init__(self, *args, **kwargs):
        super(CharFieldDisabled, self).__init__(*args, **kwargs)
        self.required = False


class EmailUserCreationForm(CoreEmailUserCreationForm):
    cnpj = BRCNPJField(label='CNPJ')

    razao_social = CharFieldDisabled(max_length=128, label='Razão Social')
    logradouro = CharFieldDisabled(max_length=128)
    numero = CharFieldDisabled(max_length=16, label='Número')
    complemento = CharFieldDisabled(max_length=64)
    cep = CharFieldDisabled(max_length=8, help_text=None, label='CEP')
    bairro = CharFieldDisabled(max_length=128)
    cidade = CharFieldDisabled(max_length=128)
    uf = CharFieldDisabled(max_length=128, label='UF')
    situacao_cadastral = CharFieldDisabled(max_length=128, label='Situação Cadastral')

    nome = CharField(max_length=128)
    sobrenome = CharField(max_length=128)
    telefone_principal = CharField(max_length=16)

    class Meta:
        model = User
        fields = ('cnpj', 'razao_social', 'logradouro', 'numero', 'complemento', 'cep', 'bairro', 'cidade', 'uf',
                  'situacao_cadastral', 'nome', 'sobrenome', 'telefone_principal', 'email',)

    def save(self, commit=True):
        user = super(EmailUserCreationForm, self).save()
        profile = user.get_profile()
        data = self.cleaned_data

        data_empresa = get_dados_empresa(data['cnpj'])

        profile.cliente_cnpj = data_empresa['cnpj']
        profile.cliente_razaosocial = data_empresa['razao_social']
        profile.cliente_logradouro = data_empresa['logradouro']
        profile.cliente_numero = data_empresa['numero']
        profile.cliente_complemento = data_empresa['complemento']
        profile.cliente_cep = data_empresa['cep']
        profile.cliente_bairro = data_empresa['bairro']
        profile.cliente_cidade = data_empresa['cidade']
        profile.cliente_uf = data_empresa['uf']
        profile.cliente_situacao_cadastral = data_empresa['situacao_cadastral']

        profile.callback_nome = data['nome']
        profile.callback_sobrenome = data['sobrenome']
        profile.callback_email_corporativo = user.email
        profile.callback_telefone_principal = data['telefone_principal']

        profile.save()

        return user
