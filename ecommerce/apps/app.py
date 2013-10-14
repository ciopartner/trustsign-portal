# -*- coding: utf-8 -*-
from oscar.app import Shop

from apps.checkout.app import application as checkout_app
from apps.customer.app import application as customer_app


class Application(Shop):
    # Use local checkout app so we can mess with the view classes
    checkout_app = checkout_app
    customer_app = customer_app

application = Application()
