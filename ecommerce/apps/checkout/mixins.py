from oscar.apps.checkout.mixins import *

class OrderPlacementMixin(OrderPlacementMixin):
    """
    Mixin which provides functionality for placing orders.
    """
    # Any payment sources should be added to this list as part of the
    # _handle_payment method.  If the order is placed successfully, then
    # they will be persisted.

    def place_order(self, order_number, user, basket, shipping_address,
                    shipping_method, total, billing_address=None, **kwargs):
        """
        Writes the order out to the DB including the payment models
        """
        # Create saved shipping address instance from passed in unsaved
        # instance
        if shipping_method.code != 'no-shipping-required':
            shipping_address = self.create_shipping_address(user, shipping_address)

        # We pass the kwargs as they often include the billing address form
        # which will be needed to save a billing address.
        billing_address = self.create_billing_address(
            billing_address, shipping_address, **kwargs)

        if 'status' not in kwargs:
            status = self.get_initial_order_status(basket)
        else:
            status = kwargs.pop('status')

        order = OrderCreator().place_order(
            user=user,
            order_number=order_number,
            basket=basket,
            shipping_address=shipping_address,
            shipping_method=shipping_method,
            total=total,
            billing_address=billing_address,
            status=status, **kwargs)
        self.save_payment_details(order)
        return order