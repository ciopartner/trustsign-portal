from oscar.apps.order.abstract_models import AbstractLine, AbstractOrder
from oscar.core.loading import get_class


class Order(AbstractOrder):
    _basket = None

    @property
    def basket(self):
        if self._basket is None:
            if self.basket_id is not None:
                Basket = get_class('basket.models', 'Basket')
                self._basket = Basket.objects.prefetch_related(
                    'lines__product__attribute_values__attribute'
                ).get(pk=self.basket_id)
        return self._basket


class Line(AbstractLine):
    def is_payment_event_permitted(self, event_type, quantity):
        return True

    def is_shipping_event_permitted(self, event_type, quantity):
        return True

from oscar.apps.order.models import *