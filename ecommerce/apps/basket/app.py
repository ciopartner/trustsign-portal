# -*- coding: utf-8 -*-
from oscar.apps.basket import views
from oscar.apps.basket.app import BasketApplication as CoreBasketApplication

from ecommerce.apps.basket.views import get_messages as local_get_messages, BasketView
views.get_messages = local_get_messages


class BasketApplication(CoreBasketApplication):
    summary_view = BasketView

application = BasketApplication()
