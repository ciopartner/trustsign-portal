# -*- coding: utf-8 -*-
from copy import deepcopy
from django.contrib import admin
from mezzanine.pages.admin import PageAdmin
from .models import Product
from .models import TabContent


class TabsInline(admin.StackedInline):
    model = TabContent
    extra = 5
    max_num = 10


class ProductAdmin(PageAdmin):
    fieldsets = deepcopy(PageAdmin.fieldsets)
    # filter_horizontal = ('tabs',)
    inlines = [TabsInline]

admin.site.register(Product, ProductAdmin)
