# -*- coding: utf-8 -*-

from oscar.apps.order.abstract_models import AbstractLine, AbstractOrder
from oscar.core.loading import get_class

Selector = get_class('partner.strategy', 'Selector')

selector = Selector()


class Order(AbstractOrder):
    _basket = None
    _lines_certificados = None
    _lines_assinaturas = None

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
        return v_stats['vouchers_issued'] > 0 and v_stats['vouchers_unused'] > 0

    @property
    def is_vouchers_issued(self):
        v_stats = self.vouchers_stats()
        return v_stats['vouchers_issued'] > 0 and v_stats['vouchers_unused'] == 0

    @property
    def get_payment_method(self):
        """
        Método responsável por retornar o nome do meio de pagamento ao template.
        """
        if hasattr(self, 'sources') and self.sources.all().exists():
            pm = self.sources.all()[0].source_type.name
            if pm == 'akatus-boleto':
                return 'Boleto'
            elif pm == 'akatus-debito':
                return 'Cartão de Débito'
            elif pm == 'akatus-credito':
                return 'Cartão de Crédito'
            else:
                return pm
        return 'Sem Informações de Pagamento'

    def get_lines_certificados(self):
        if self._lines_certificados is None:
            Basket = get_class('basket.models', 'Basket')
            self._lines_certificados = self._get_lines_category(
                category=[Basket.CATEGORIA_CERTIFICADO, Basket.CATEGORIA_CERT_ITENS_ADICIONAIS],
                category_negative=[Basket.CATEGORIA_ASSINATURA])
        return self._lines_certificados

    def get_lines_assinaturas(self):
        if self._lines_assinaturas is None:
            Basket = get_class('basket.models', 'Basket')
            self._lines_assinaturas = self._get_lines_category(
                category=[Basket.CATEGORIA_ASSINATURA],
                category_negative=[Basket.CATEGORIA_CERTIFICADO, Basket.CATEGORIA_CERT_ITENS_ADICIONAIS])
        return self._lines_assinaturas

    def _get_lines_category(self, category=None, category_negative=None):

        category = category or []
        category_negative = category_negative or []

        return [line for line in self.lines.select_related('product')
                if line.product.categories.filter(slug__in=category).exclude(slug__in=category_negative).exists()]

    @property
    def num_items_certificados(self):
        return sum(line.quantity for line in self.get_lines_certificados())

    @property
    def num_items_assinaturas(self):
        return sum(line.quantity for line in self.get_lines_assinaturas())


class Line(AbstractLine):
    def is_payment_event_permitted(self, event_type, quantity):
        return True

    def is_shipping_event_permitted(self, event_type, quantity):
        return True

from oscar.apps.order.models import *