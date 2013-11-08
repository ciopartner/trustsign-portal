from django.contrib.auth import get_user_model
from django.db.models import ForeignKey, CharField, DateField, TextField, Model, DateTimeField
from oscar.apps.payment.abstract_models import AbstractBankcard, AbstractTransaction, AbstractSource
User = get_user_model()


class Source(AbstractSource):

    def create_deferred_transaction(self, txn_type, amount, reference=None,
                                    status=None, bankcard=None, debitcard=None, boleto=None):
        """
        Register the data for a transaction that can't be created yet due to FK
        constraints.  This happens at checkout where create an payment source
        and a transaction but can't save them until the order model exists.
        """
        if self.deferred_txns is None:
            self.deferred_txns = []
        self.deferred_txns.append((txn_type, amount, reference, status, bankcard, debitcard, boleto))

    def _create_transaction(self, txn_type, amount, reference='',
                            status='', bankcard=None, debitcard=None, boleto=None):
        self.transactions.create(
            txn_type=txn_type, amount=amount,
            reference=reference, status=status, bankcard=bankcard, debitcard=debitcard, boleto=boleto)


class Transaction(AbstractTransaction):
    bankcard = ForeignKey('payment.Bankcard', related_name='sources', blank=True, null=True)
    debitcard = ForeignKey('payment.Debitcard', related_name='sources', blank=True, null=True)
    boleto = ForeignKey('payment.Boleto', related_name='sources', blank=True, null=True)
    date_approved = DateTimeField(blank=True, null=True)


class Bankcard(AbstractBankcard):
    credito_cpf = CharField(max_length=16, blank=True, null=True)
    credito_telefone = CharField(max_length=16, blank=True, null=True)


class Debitcard(Model):
    user = ForeignKey(User, related_name='debitcards', blank=True, null=True)
    banco = CharField(max_length=16)
    agencia = CharField(max_length=8, blank=True, null=True)
    conta = CharField(max_length=16, blank=True, null=True)
    debitcard_url = CharField(max_length=256, blank=True, null=True)


class Boleto(Model):
    user = ForeignKey(User, related_name='boletos', blank=True, null=True)
    nosso_numero = CharField(max_length=32, blank=True, null=True)
    vencimento = DateField(blank=True, null=True)
    boleto_html = TextField(blank=True, null=True)
    boleto_url = CharField(max_length=256, blank=True, null=True)


from oscar.apps.payment.models import *