from django.contrib import admin
from portal.banners.models import Banners


class BannerAmin(admin.ModelAdmin):
    pass

admin.site.register(Banners, BannerAmin)