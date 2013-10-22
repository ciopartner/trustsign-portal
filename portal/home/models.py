# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db.models import OneToOneField, DateField, TextField, PositiveSmallIntegerField, CharField, Model, EmailField
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


class TrustSignProfile(Model):
    PERFIL_CLIENTE = 1
    PERFIL_PLATAFORMA = 2
    PERFIL_TRUSTSIGN = 3
    PERFIL_CHOICES = (
        (PERFIL_CLIENTE, 'Cliente'),
        (PERFIL_PLATAFORMA, 'Plataforma'),
        (PERFIL_TRUSTSIGN, 'Trustsign'),
    )

    user = OneToOneField(User)
    date_of_birth = DateField(blank=True, null=True)
    bio = TextField(blank=True, default='')
    tagline = TextField(blank=True, default='')

    cliente_cnpj = CharField(max_length=32, blank=True, default='')
    cliente_razaosocial = CharField(max_length=128, blank=True, default='')
    cliente_logradouro = CharField(max_length=128, blank=True, default='')
    cliente_numero = CharField(max_length=16, blank=True, default='')
    cliente_complemento = CharField(max_length=64, blank=True, default='')
    cliente_cep = CharField(max_length=8, blank=True, default='')
    cliente_bairro = CharField(max_length=128, blank=True, default='')
    cliente_cidade = CharField(max_length=128, blank=True, default='')
    cliente_uf = CharField(max_length=128, blank=True, default='')
    cliente_situacao_cadastral = CharField(max_length=128, blank=True, default='')

    callback_nome = CharField(max_length=128, blank=True, default='')
    callback_sobrenome = CharField(max_length=128, blank=True, default='')
    callback_email_corporativo = EmailField(blank=True, default='')
    callback_telefone_principal = CharField(max_length=16, blank=True, default='')

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


def create_profile(sender, **kwargs):
    if kwargs["created"]:
        profile = TrustSignProfile(user=kwargs['instance'])
        profile.save()

post_save.connect(create_profile, sender=User, dispatch_uid='home.models.create_profile')