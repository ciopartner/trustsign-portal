# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import CharField, TextInput, BooleanField, ChoiceField
from localflavor.br.forms import BRCNPJField
from oscar.apps.customer.forms import EmailUserCreationForm as CoreEmailUserCreationForm, \
    ProfileForm as CoreProfileForm, EmailAuthenticationForm as CoreEmailAuthenticationForm
from ecommerce.website.utils import get_dados_empresa, limpa_cnpj
from portal.home.models import TrustSignProfile

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


class EmailAuthenticationForm(CoreEmailAuthenticationForm):
    username = BRCNPJField(label='CNPJ', widget=TextInput(attrs={'class': 'mask-cnpj'}))

    def clean_username(self):
        username = self.cleaned_data['username']
        return limpa_cnpj(username)


class EmailUserCreationForm(CoreEmailUserCreationForm):
    cnpj = BRCNPJField(label='CNPJ', widget=TextInput(attrs={'class': 'mask-cnpj'}))

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

    cliente_ecommerce = BooleanField(label='e-commerce', help_text='Seu site realiza operações de e-commerce?', required=False)
    cliente_tipo_negocio = ChoiceField(label='Tipo do Negócio', choices=TrustSignProfile.TIPO_NEGOCIO_CHOICES)
    cliente_fonte_potencial = ChoiceField(label='Fonte do Potencial', choices=TrustSignProfile.FONTE_POTENCIAL_CHOICES)

    class Meta:
        model = User
        fields = ('cnpj', 'razao_social', 'logradouro', 'numero', 'complemento', 'cep', 'bairro', 'cidade', 'uf',
                  'situacao_cadastral', 'cliente_tipo_negocio', 'cliente_fonte_potencial', 'cliente_ecommerce', 'nome',
                  'sobrenome', 'telefone_principal', 'email',)

    def clean_cnpj(self):
        cnpj = self.cleaned_data['cnpj']

        if User.objects.filter(username=limpa_cnpj(cnpj)).exists():
            raise ValidationError('Já existe um usuário cadastrado com esse CNPJ')

        return cnpj

    def save(self, commit=True):
        data = self.cleaned_data
        data_empresa = get_dados_empresa(data['cnpj'])

        user = super(EmailUserCreationForm, self).save(commit=False)

        user.username = data_empresa['cnpj']  # cnpj sem mascara
        user.first_name = data['nome']
        user.last_name = data['sobrenome']
        user.save()

        profile = user.get_profile()

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

        profile.cliente_ecommerce = data['cliente_ecommerce']
        profile.cliente_tipo_negocio = data['cliente_tipo_negocio']
        profile.cliente_fonte_potencial = data['cliente_fonte_potencial']

        profile.callback_nome = data['nome']
        profile.callback_sobrenome = data['sobrenome']
        profile.callback_email_corporativo = user.email
        profile.callback_telefone_principal = data['telefone_principal']

        profile.save()

        return user


class ProfileForm(CoreProfileForm):

    class Meta(CoreProfileForm.Meta):
        exclude = ['user', 'date_of_birth', 'perfil', 'cliente_cnpj',
                   'cliente_razaosocial', 'cliente_logradouro', 'cliente_numero', 'cliente_complemento', 'cliente_cep',
                   'cliente_bairro', 'cliente_cidade', 'cliente_uf', 'cliente_situacao_cadastral', 'bio', 'tagline']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        # adicionados dinamicamente no super:
        del self.fields['email']
        del self.fields['first_name']
        del self.fields['last_name']

        self.user_field_names = ()

    def save(self, *args, **kwargs):
        profile = super(ProfileForm, self).save(*args, **kwargs)

        user = profile.user
        user.first_name = profile.callback_nome
        user.last_name = profile.callback_sobrenome
        user.save()

        return profile