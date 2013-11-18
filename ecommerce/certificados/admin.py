# -*- coding: utf-8 -*-
from django.contrib import admin
from ecommerce.certificados.models import Voucher, Emissao, Revogacao


class EmissaoAdmin(admin.ModelAdmin):
    list_display = ('crm_hash', 'emission_primary_dn', 'emission_status')
admin.site.register(Emissao, EmissaoAdmin)

admin.site.register(Revogacao)

class VoucherAdmin(admin.ModelAdmin):
    list_display = ('crm_hash', 'order_number', 'order_date', 'customer_cnpj', 'ssl_product', 'ssl_line', 'ssl_term',
                    'comodo_order')
    ordering = ['-order_number']
admin.site.register(Voucher, VoucherAdmin)