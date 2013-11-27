from decimal import Decimal
from django.utils import timezone
from oscar.apps.partner import strategy, prices
from oscar.core.loading import get_class

FixedPriceOffer = get_class('offer.models', 'FixedPriceOffer')


class Selector(object):
    """
    Custom selector to return a fixed offer strategy
    """

    def strategy(self, request=None, user=None, **kwargs):
        return FixedOfferStrategy(request)


class FixedPriceWithDiscount(prices.FixedPrice):

    def __init__(self, price_regular, currency, excl_tax, tax=None):
        self.price_regular = price_regular
        super(FixedPriceWithDiscount, self).__init__(currency, excl_tax, tax)


class FixedOfferStrategy(strategy.Default):
    """

    """
    def pricing_policy(self, product, stockrecord):
        if not stockrecord:
            return prices.Unavailable()

        now = timezone.now()
        fixed_offers = product.fixed_price_offer_items.filter(
            offer__status=FixedPriceOffer.OPEN,
            offer__start_datetime__lte=now,
            offer__end_datetime__gte=now
        )
        if fixed_offers:
            return FixedPriceWithDiscount(
                price_regular=stockrecord.price_excl_tax,
                currency=stockrecord.price_currency,
                excl_tax=min(offer.price_discount for offer in fixed_offers),
                tax=Decimal('0.00')
            )
        return FixedPriceWithDiscount(
            price_regular=None,
            currency=stockrecord.price_currency,
            excl_tax=stockrecord.price_excl_tax,
            tax=Decimal('0.00')
        )