# -*- coding: utf-8 -*-
from oscar.app import Shop

from ecommerce.apps.checkout.app import application as local_checkout_app
from ecommerce.apps.customer.app import application as local_customer_app
from ecommerce.apps.basket.app import application as local_basket_app


class Application(Shop):
    # Use local checkout app so we can mess with the view classes
    checkout_app = local_checkout_app
    customer_app = local_customer_app
    basket_app   = local_basket_app

application = Application()
