from django.db.models import CharField
from oscar.apps.catalogue.abstract_models import AbstractProduct


class Product(AbstractProduct):
    product_code = CharField(max_length=16, blank=True, null=True)
    product_line = CharField(max_length=16, blank=True, null=True)
    product_term = CharField(max_length=16, blank=True, null=True)

    def get_absolute_url(self):
        return '/portal/certificado-digital/%s/' % self.product_code


from oscar.apps.catalogue.models import *