from oscar.apps.order.processing import EventHandler as CoreEventHandler
from libs.crm.mixins import OscarToCRMMixin


class EventHandler(CoreEventHandler, OscarToCRMMixin):
    def handle_shipping_event(self, order, event_type, lines, line_quantities, **kwargs):
        self.validate_shipping_event(order, event_type, lines, line_quantities, **kwargs)
        print 'entroooooooooooooooooooou'
        #self.send_order_to_crm(order)
        self.create_shipping_event(order, event_type, lines, line_quantities, **kwargs)

    def handle_payment_event(self, order, event_type, amount, lines=None, line_quantities=None, **kwargs):
        print 11111111111111
        super(EventHandler, self).handle_payment_event(order, event_type, amount, lines, line_quantities, **kwargs)
        print 2222222222222222222