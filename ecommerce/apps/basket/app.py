from oscar.apps.basket import views
from oscar.apps.basket.app import BasketApplication as CoreBasketApplication

from ecommerce.apps.basket.views import get_messages as local_get_messages
views.get_messages = local_get_messages

class BasketApplication(CoreBasketApplication):
    summary_view = views.BasketView

application = BasketApplication()
