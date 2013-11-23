# -*- coding: utf-8 -*-
from django.db.models.signals import post_save

from oscar.apps.order.abstract_models import AbstractLine, AbstractOrder
from oscar.core.loading import get_class
from ecommerce.website.utils import send_template_email

Selector = get_class('partner.strategy', 'Selector')

selector = Selector()


class Order(AbstractOrder):
    _basket = None

    @property
    def basket(self):
        if self._basket is None:
            if self.basket_id is not None:
                Basket = get_class('basket.models', 'Basket')
                self._basket = Basket.objects.prefetch_related(
                    'lines__product__attribute_values__attribute'
                ).get(pk=self.basket_id)
                self._basket.strategy = selector.strategy()
        return self._basket

    @property
    def is_order_placed(self):
        return True

    @property
    def is_order_paid(self):
        STATUS_PAID = ['Pago', 'Em Processamento', 'Concluído']
        return self.status in STATUS_PAID

    def vouchers_stats(self):
        vouchers = self.vouchers.all()
        vouchers_issued = 0
        vouchers_unused = 0
        for voucher in vouchers:
            if hasattr(voucher, 'emissao'):
                vouchers_issued += 1
            else:
                vouchers_unused += 1
        return {'vouchers_issued': vouchers_issued, 'voucher_unused': vouchers_unused}

    @property
    def is_vouchers_partially_issued(self):
        """
        Retorna verdadeiro se a ordem possui algum voucher emitido, porém não todos.
        """
        v_stats = self.vouchers_stats()
        return (v_stats['vouchers_issued'] > 0 and v_stats['vouchers_unused'] > 0)

    @property
    def is_vouchers_issued(self):
        v_stats = self.vouchers_stats()
        return (v_stats['vouchers_issued'] > 0 and v_stats['vouchers_unused'] == 0)

    @property
    def get_payment_method(self):
        """
        Método responsável por retornar o nome do meio de pagamento ao template.
        """
        if hasattr(self, 'sources') and self.sources.all().exists():
            pm = self.sources.all()[0].source_type.name
            if pm=='akatus-boleto':
                return 'Boleto'
            elif pm=='akatus-debito':
                return 'Cartão de Débito'
            elif pm=='akatus-credito':
                return 'Cartão de Crédito'
            else:
                return pm
        return 'Sem Informações de Pagamento'

class Line(AbstractLine):
    def is_payment_event_permitted(self, event_type, quantity):
        return True

    def is_shipping_event_permitted(self, event_type, quantity):
        return True

def send_email_order_placed(sender, instance, **kwargs):
    """
    Send the order placed e-mail
    """
    order = instance
    subject = 'Pedido Realizado com Sucesso'
    template = 'customer/emails/commtype_order_placed_body.html'
    context = {
        'user': order.user,
        'order': order,
        'site': order.site.domain,
    }
    if kwargs.get('created', True):
        send_template_email([order.user.email], subject, template, context)


# Register a signal to send the Pedido Realizado com Sucesso
post_save.connect(send_email_order_placed, sender=Order, dispatch_uid="email_order_placed")

from oscar.apps.order.models import *