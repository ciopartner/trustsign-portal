from django.db.models import ForeignKey
from oscar.apps.payment.abstract_models import AbstractSource


class Source(AbstractSource):
    bankcard = ForeignKey('payment.Bankcard', related_name='sources', blank=True, null=True)

from oscar.apps.payment.models import *