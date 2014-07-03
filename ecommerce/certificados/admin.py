# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from copy import copy
from django.contrib import admin
from django.core.urlresolvers import reverse
from ecommerce.certificados.models import Voucher, Emissao, Revogacao, VoucherAuditoria


class EmissaoAdmin(admin.ModelAdmin):
    list_display = ('crm_hash', 'emission_primary_dn', 'emission_status')


class VoucherAdmin(admin.ModelAdmin):
    list_display = ('crm_hash', 'order_number', 'order_date', 'customer_cnpj', 'ssl_product', 'ssl_line', 'ssl_term',
                    'comodo_order')
    ordering = ['-order_number']
    search_fields = ['customer_cnpj', 'order_number', 'crm_hash', 'customer_companyname']


class EmissaoInline(admin.StackedInline):
    model = Emissao
    extra = 0
    fields = [
        'comodo_order', 'requestor_user', 'emission_url', 'emission_urls', 'emission_csr', 'emission_dcv_emails',
        'emission_publickey_sendto', 'emission_server_type', 'emission_reviewer', 'emission_approver',
        'emission_primary_dn', 'emission_assignment_letter_link', 'emission_articles_of_incorporation_link',
        'emission_address_proof_link', 'emission_ccsa_link', 'emission_evcr_link', 'emission_phone_proof_link',
        'emission_id_link', 'emission_cost', 'emission_status', 'emission_error_message', 'emission_certificate'
    ]
    readonly_fields = copy(fields)


class VoucherAuditoriaAdmin(admin.ModelAdmin):
    list_display = ['customer_cnpj', 'emission_url', 'comodo_order', 'order_number', 'ssl_product', 'ssl_line',
                    'ssl_term', 'emission_status', 'order_date', 'revogado']
    inlines = [EmissaoInline]
    search_fields = ['crm_hash', 'customer_cnpj', 'customer_companyname', 'customer_callback_email',
                     'comodo_order', 'order_number']
    list_filter = ['emissao__emission_status']
    list_select_related = True
    fields = [
        'crm_user', 'comodo_order', 'order_number', 'customer_cnpj', 'customer_companyname',
        'customer_registration_status', 'customer_callback_email', 'ssl_code', 'ssl_url',
        'ssl_product', 'ssl_line', 'ssl_term', 'ssl_valid_from', 'ssl_valid_to', 'ssl_publickey', 'ssl_revoked_date',
        'ssl_domains_qty', 'ssl_key_size', 'order', 'order_line', 'order_date',
        'order_item_value', 'order_channel', 'order_canceled_date', 'order_canceled_reason'
    ]
    readonly_fields = copy(fields)
    date_hierarchy = 'order_date'

    def emission_url(self, obj):
        if obj.emissao:
            return obj.emissao.emission_url
        return ''

    def emission_status(self, obj):
        if obj.emissao:
            return obj.emissao.get_emission_status_display()
        return ''

    def revogado(self, obj):
        if hasattr(obj, 'emissao') and obj.emissao and obj.emissao.emission_status == Emissao.STATUS_REVOGADO:
            revogacoes = obj.emissao.revogacoes.all()
            if revogacoes:
                return 'Sim - <a href="{}">Link</a>'.format(reverse('admin:certificados_revogacao_change', args=[revogacoes[0].pk]))
            return 'Sim'
        return 'Não'
    revogado.allow_tags = True

admin.site.register(Emissao, EmissaoAdmin)
admin.site.register(Voucher, VoucherAdmin)
admin.site.register(Revogacao)
admin.site.register(VoucherAuditoria, VoucherAuditoriaAdmin)