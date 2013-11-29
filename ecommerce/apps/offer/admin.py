from django.forms import ModelForm
from oscar.apps.offer.admin import *
from oscar.core.loading import get_class
from ecommerce.apps.offer.models import FixedPriceOffer, FixedPriceOfferItem


Product = get_class('catalogue.models', 'Product')


class FixedPriceOfferItemForm(ModelForm):
    class Meta:
        model = FixedPriceOfferItem

    def __init__(self, **kwargs):
        super(FixedPriceOfferItemForm, self).__init__(**kwargs)
        self.fields['product'].queryset = Product.objects.order_by('title')


class FixedPriceOfferItemInline(admin.TabularInline):
    model = FixedPriceOfferItem
    form = FixedPriceOfferItemForm


class FixedPriceOfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_datetime', 'end_datetime', 'status', '_quantidade_produtos']
    inlines = (FixedPriceOfferItemInline,)

    def _quantidade_produtos(self, obj):
        return obj.items.count()


class FixedPriceOfferItemAdmin(admin.ModelAdmin):
    list_display = ['offer', 'product', 'price_discount']


admin.site.register(FixedPriceOffer, FixedPriceOfferAdmin)
admin.site.register(FixedPriceOfferItem, FixedPriceOfferItemAdmin)