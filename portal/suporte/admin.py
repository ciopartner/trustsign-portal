from django.contrib import admin
from mezzanine.pages.admin import PageAdmin
from portal.suporte.models import Manual, ManualPage, Item, GlossarioPage, FAQPage, Question


class ManualAdminInline(admin.TabularInline):
    model = Manual


class ManualPageAdmin(PageAdmin):
    inlines = (ManualAdminInline, )


class ItemAdminInline(admin.TabularInline):
    model = Item


class GlossarioPageAdmin(PageAdmin):
    inlines = (ItemAdminInline, )


class QuestionAdminInline(admin.TabularInline):
    model = Question


class FAQPageAdmin(PageAdmin):
    inlines = [QuestionAdminInline]


admin.site.register(FAQPage, FAQPageAdmin)
admin.site.register(ManualPage, ManualPageAdmin)
admin.site.register(GlossarioPage, GlossarioPageAdmin)