# -*- coding: utf-8 -*-
from oscar.apps.checkout import app

from ecommerce.apps.checkout import views


class CheckoutApplication(app.CheckoutApplication):
    # Replace the payment details view with our own
    payment_details_view = views.PaymentDetailsView

application = CheckoutApplication()