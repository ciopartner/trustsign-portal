# -*- coding: utf-8 -*-
from oscar.apps.checkout import app
from ecommerce.apps.checkout.akatus import views


class CheckoutApplication(app.CheckoutApplication):
    # Replace the payment details view with our own
    payment_details_view = views.PaymentDetailsView
    shipping_address_view = views.ShippingAddressView
    thankyou_view = views.ThankYouView


application = CheckoutApplication()