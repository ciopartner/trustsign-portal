# -*- coding: utf-8 -*-
from django.contrib import admin
from ecommerce.certificados.models import Voucher, Emissao, Revogacao

admin.site.register(Emissao)
admin.site.register(Revogacao)
admin.site.register(Voucher)