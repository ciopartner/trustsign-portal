# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from copy import copy
from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from ecommerce.certificados.models import Voucher, Emissao, Revogacao, VoucherAuditoria, EmissaoManual


class EmissaoAdmin(admin.ModelAdmin):
    list_display = ('crm_hash', 'emission_primary_dn', 'emission_status')


class VoucherAdmin(admin.ModelAdmin):
    list_display = ('crm_hash', 'order_number', 'order_date', 'customer_cnpj', 'ssl_product', 'ssl_line', 'ssl_term',
                    'comodo_order')
    ordering = ['-order_number']
    search_fields = ['customer_cnpj', 'order_number', 'crm_hash', 'customer_companyname']
    actions = ['emissao_manual']

    def emissao_manual(self, request, queryset):
        if len(queryset) != 1:
            messages.error(request, 'Inicie a emissão manual de um voucher por vez')
            return

        voucher = queryset[0]

        try:
            if voucher.emissao:
                emissao = voucher.emissao
                if emissao.emission_status != Emissao.STATUS_EMISSAO_MANUAL:
                    messages.error(request, 'Este voucher já possui uma emissão')
                    return
                return HttpResponseRedirect(reverse('admin:certificados_emissaomanual_change', args=[emissao.pk]))
        except Emissao.DoesNotExist:
            pass

        emissao = Emissao.objects.create(
            voucher=voucher,
            crm_hash=voucher.crm_hash,
            requestor_user=request.user,
            emission_status=Emissao.STATUS_EMISSAO_MANUAL,
        )

        return HttpResponseRedirect(reverse('admin:certificados_emissaomanual_change', args=[emissao.pk]))

    emissao_manual.short_description = 'Iniciar Emissão Manual'


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
    list_select_related = True
    fields = [
        'crm_user', 'comodo_order', 'order_number', 'customer_cnpj', 'customer_companyname',
        'customer_callback_email', 'ssl_code', 'ssl_url', 'ssl_product', 'ssl_line', 'ssl_term',
        'ssl_valid_from', 'ssl_valid_to', 'ssl_publickey', 'ssl_revoked_date',
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


class EmissaoManualAdmin(admin.ModelAdmin):
    fields = ['comodo_order', 'emission_url', 'emission_urls', 'emission_dcv_emails', 'emission_publickey_sendto',
              'emission_server_type', 'emission_assignment_letter', 'emission_articles_of_incorporation',
              'emission_address_proof', 'emission_ccsa', 'emission_evcr', 'emission_phone_proof', 'emission_id',
              'emission_status', 'emission_csr', 'emission_certificate']
    readonly_fields = ['emission_status']

admin.site.register(Emissao, EmissaoAdmin)
admin.site.register(EmissaoManual, EmissaoManualAdmin)
admin.site.register(Voucher, VoucherAdmin)
admin.site.register(Revogacao)
admin.site.register(VoucherAuditoria, VoucherAuditoriaAdmin)