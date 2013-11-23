# -*- coding: utf-8 -*-

from oscar.apps.order.abstract_models import AbstractLine, AbstractOrder
from oscar.core.loading import get_class
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
        return False
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
        if hasattr(self, 'sources'):
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

from oscar.apps.order.models import *