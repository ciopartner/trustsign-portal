from oscar.apps.order.abstract_models import AbstractLine


class Line(AbstractLine):
    def is_payment_event_permitted(self, event_type, quantity):
        return True

    def is_shipping_event_permitted(self, event_type, quantity):
        return True

from oscar.apps.order.models import *