# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db.models import OneToOneField, DateField, TextField, PositiveSmallIntegerField, CharField, Model, EmailField, BooleanField, ImageField
from django.db.models.signals import post_save

# The members of Page will be inherited by the Author model, such
# as title, slug, etc. For authors we can use the title field to
# store the author's name. For our model definition, we just add
# any extra fields that aren't part of the Page model, in this
# case, date of birth.

# class Home(Page):
#
#     dob = models.DateField("Date of birth")
#
# class Book(models.Model):
#     author = models.ForeignKey("Author")
#     cover = models.ImageField(upload_to="authors")
from ecommerce.website.utils import formata_cnpj


class TrustSignProfile(Model):
    PERFIL_CLIENTE = 1
    PERFIL_PLATAFORMA = 2
    PERFIL_TRUSTSIGN = 3
    PERFIL_CHOICES = (
        (PERFIL_CLIENTE, 'Cliente'),
        (PERFIL_PLATAFORMA, 'Plataforma'),
        (PERFIL_TRUSTSIGN, 'Trustsign'),
    )

    TIPO_NEGOCIO_CHOICES = (
        ('Communications', 'Comunicações'),
        ('Consulting', 'Consultoria'),
        ('Energy', 'Energia'),
        ('Engineering', 'Engenharia'),
        ('Education', 'Ensino'),
        ('Finance', 'Financeira'),
        ('Government', 'Governo'),
        ('Other', 'Outros'),
        ('Industry', 'Industria'),
        ('Healthcare', 'Saúde'),
        ('Insurance', 'Seguros'),
        ('Not For Profit', 'Sem Fins Lucrativos'),
        ('Servicos', 'Serviços'),
        ('Technology', 'Tecnologia'),
        ('Telecommunications', 'Telecomunicações'),
        ('Transportation', 'Transportes'),
        ('Turismo', 'Turismo'),
        ('Retail', 'Varejo'),
    )
    FONTE_POTENCIAL_CHOICES = (
        ('Abraweb', 'Abraweb'),
        ('Acoes de Marketing', 'Ações de Marketing'),
        ('Buscadores', 'Buscadores'),
        ('ECommerce Brasil', 'E-Commerce Brasil'),
        ('Eventos', 'Eventos'),
        ('Site de Clientes', 'Site de Clientes'),
        ('Website', 'Website'),
    )

    user = OneToOneField(User)
    foto = ImageField(upload_to='profiles/fotos', blank=True, null=True)
    date_of_birth = DateField(blank=True, null=True)
    bio = TextField(blank=True, default='')
    tagline = TextField(blank=True, default='')
    email_nfe = EmailField(blank=True, default='', verbose_name='e-Mail p/ envio da NFe')

    cliente_cnpj = CharField(max_length=32, blank=True, default='')
    cliente_razaosocial = CharField(max_length=128, blank=True, default='')
    cliente_nomefantasia = CharField(max_length=128, blank=True, default='')
    cliente_logradouro = CharField(max_length=128, blank=True, default='')
    cliente_numero = CharField(max_length=16, blank=True, default='')
    cliente_complemento = CharField(max_length=64, blank=True, default='')
    cliente_cep = CharField(max_length=8, blank=True, default='')
    cliente_bairro = CharField(max_length=128, blank=True, default='')
    cliente_cidade = CharField(max_length=128, blank=True, default='')
    cliente_uf = CharField(max_length=128, blank=True, default='')
    cliente_situacao_cadastral = CharField(max_length=128, blank=True, default='')

    callback_nome = CharField(max_length=128, blank=True, default='', verbose_name='nome')
    callback_sobrenome = CharField(max_length=128, blank=True, default='', verbose_name='sobrenome')
    callback_email_corporativo = EmailField(blank=True, default='', verbose_name='e-mail corporativo')
    callback_telefone_principal = CharField(max_length=16, blank=True, default='', verbose_name='telefone principal')

    cliente_ecommerce = BooleanField(default=False, verbose_name='e-commerce', help_text='Seu site realiza operações de e-commerce?', blank=True)
    cliente_tipo_negocio = CharField(max_length=128, verbose_name='Tipo do Negócio', choices=TIPO_NEGOCIO_CHOICES, default='Other', blank=True)
    cliente_fonte_potencial = CharField(max_length=128, verbose_name='Como chegou até nós?', choices=FONTE_POTENCIAL_CHOICES, default='Website', blank=True)

    perfil = PositiveSmallIntegerField(choices=PERFIL_CHOICES, default=PERFIL_CLIENTE)

    def __unicode__(self):
        return 'Profile: %s' % self.user

    @property
    def is_trustsign(self):
        return self.perfil == self.PERFIL_TRUSTSIGN

    @property
    def is_cliente(self):
        return self.perfil == self.PERFIL_CLIENTE

    @property
    def is_plataforma(self):
        return self.perfil == self.PERFIL_PLATAFORMA

    def get_cnpj_formatado(self):
        if len(self.cliente_cnpj) == 14:
            return formata_cnpj(self.cliente_cnpj)
        return self.cliente_cnpj


def create_profile(sender, **kwargs):
    if kwargs["created"]:
        profile = TrustSignProfile(user=kwargs['instance'])
        profile.save()

post_save.connect(create_profile, sender=User, dispatch_uid='home.models.create_profile')