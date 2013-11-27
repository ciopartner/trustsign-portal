from oscar.apps.offer.admin import *
from ecommerce.apps.offer.models import FixedPriceOffer, FixedPriceOfferItem


class FixedPriceOfferItemInline(admin.TabularInline):
    model = FixedPriceOfferItem


class FixedPriceOfferAdmin(admin.ModelAdmin):
    inlines = (FixedPriceOfferItemInline,)


admin.site.register(FixedPriceOffer, FixedPriceOfferAdmin)
admin.site.register(FixedPriceOfferItem)