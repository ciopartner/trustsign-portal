from oscar.apps.order.processing import EventHandler as CoreEventHandler
from libs.crm.mixins import OscarToCRMMixin


class EventHandler(CoreEventHandler, OscarToCRMMixin):
    def handle_shipping_event(self, order, event_type, lines, line_quantities, **kwargs):
        self.validate_shipping_event(order, event_type, lines, line_quantities, **kwargs)
        #self.send_order_to_crm(order)
        self.create_shipping_event(order, event_type, lines, line_quantities, **kwargs)