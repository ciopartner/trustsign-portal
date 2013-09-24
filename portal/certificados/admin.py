from django.contrib import admin
from portal.certificados.models import Voucher, Emissao, Revogacao

admin.site.register(Emissao)
admin.site.register(Revogacao)
admin.site.register(Voucher)