from django.db.models import ForeignKey, CharField, DateField, TextField, Model, DateTimeField
from oscar.apps.payment.abstract_models import AbstractBankcard, AbstractTransaction


class Transaction(AbstractTransaction):
    bankcard = ForeignKey('payment.Bankcard', related_name='sources', blank=True, null=True)
    debitcard = ForeignKey('payment.Debitcard', related_name='sources', blank=True, null=True)
    boleto = ForeignKey('payment.Boleto', related_name='sources', blank=True, null=True)
    date_approved = DateTimeField(blank=True, null=True)


class Bankcard(AbstractBankcard):
    credito_cpf = CharField(max_length=16, blank=True, null=True)
    credito_telefone = CharField(max_length=16, blank=True, null=True)


class Debitcard(Model):
    banco = CharField(max_length=16)
    agencia = CharField(max_length=8, blank=True, null=True)
    conta = CharField(max_length=16, blank=True, null=True)


class Boleto(Model):
    nosso_numero = CharField(max_length=32)
    vencimento = DateField()
    boleto_html = TextField()


from oscar.apps.payment.models import *