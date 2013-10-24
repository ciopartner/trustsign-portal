# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from oscar.apps.catalogue.abstract_models import AbstractProduct


class Product(AbstractProduct):

    def get_absolute_url(self):
        return '/portal/certificado-digital/%s/' % self.attr.ssl_code


from oscar.apps.catalogue.models import *