from mezzanine.pages.admin import PageAdmin
from portal.ferramentas.models import FerramentasPage
from django.contrib import admin


admin.site.register(FerramentasPage, PageAdmin)