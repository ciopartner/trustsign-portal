from django.db.models import CharField
from oscar.apps.catalogue.abstract_models import AbstractProduct


class Product(AbstractProduct):
    product_code = CharField(max_length=16, blank=True, null=True)
    product_line = CharField(max_length=16, blank=True, null=True)
    product_term = CharField(max_length=16, blank=True, null=True)


from oscar.apps.catalogue.models import *