# -*- coding: utf-8 -*-
from copy import deepcopy
from django.contrib import admin
from mezzanine.pages.admin import PageAdmin
from .models import Product
from .models import TabContent
from .models import Question,FAQPage 


class TabsInline(admin.StackedInline):
    model = TabContent
    extra = 5
    max_num = 10


class ProductAdmin(PageAdmin):
    fieldsets = deepcopy(PageAdmin.fieldsets)
    # filter_horizontal = ('tabs',)
    inlines = [TabsInline]


class QuestionAdminInline(admin.TabularInline):
    model = Question


class FAQPageAdmin(PageAdmin):
    inlines = [QuestionAdminInline]


admin.site.register(Product, ProductAdmin)
admin.site.register(FAQPage, FAQPageAdmin)
