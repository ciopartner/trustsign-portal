# -*- coding: utf-8 -*-
from django.contrib import admin
from mezzanine.pages.admin import PageAdmin
from .models import Wizard


class WizardAdmin(PageAdmin):
    pass


admin.site.register(Wizard, WizardAdmin)