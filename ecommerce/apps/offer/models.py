from django.core.exceptions import ValidationError
from django.db.models import Model, CharField, DateTimeField, ForeignKey, DecimalField, ImageField
from django.utils.translation import ugettext as _


class FixedPriceOffer(Model):
    """
    A fixed price offer cause Oscar doesn't have one yet
    """
    OPEN, SUSPENDED = "Open", "Suspended"
    status = CharField(max_length=64, default=OPEN)

    start_datetime = DateTimeField(blank=True, null=True)
    end_datetime = DateTimeField(blank=True, null=True, help_text=_("Offers are active until the end of the 'end date'"))

    label = ImageField(upload_to='offers/labels', blank=True, null=True)

    def clean(self):
        if (self.start_datetime and self.end_datetime and
            self.start_datetime > self.end_datetime):
            raise ValidationError(
                _('End date should be later than start date'))

    @property
    def is_open(self):
        return self.status == self.OPEN

    @property
    def is_suspended(self):
        return self.status == self.SUSPENDED

    def suspend(self):
        self.status = self.SUSPENDED
        self.save()
    suspend.alters_data = True

    def unsuspend(self):
        self.status = self.OPEN
        self.save()
    suspend.alters_data = True


class FixedPriceOfferItem(Model):
    offer = ForeignKey('offer.FixedPriceOffer', related_name='items')
    product = ForeignKey('catalogue.Product', related_name='fixed_price_offer_items')
    price_discount = DecimalField(max_digits=12, decimal_places=2)


from oscar.apps.offer.models import *