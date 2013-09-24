from django.contrib import admin
from portal.certificados.models import Voucher, Emissao

admin.site.register(Emissao)
admin.site.register(Voucher)