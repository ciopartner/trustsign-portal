from oscar.apps.basket.abstract_models import AbstractBasket


class Basket(AbstractBasket):
    _tem_contrato_ssl = None
    _tem_contrato_siteseguro = None
    _tem_contrato_sitemonitorado = None
    _tem_contrato_pki = None

    def tem_contrato_ssl(self):
        if self._tem_contrato_ssl is None:
            from ecommerce.certificados.models import Voucher
            codigos = (
                Voucher.PRODUTO_SSL, Voucher.PRODUTO_SSL_WILDCARD, Voucher.PRODUTO_SAN_UCC, Voucher.PRODUTO_EV,
                Voucher.PRODUTO_EV_MDC, Voucher.PRODUTO_MDC, Voucher.PRODUTO_CODE_SIGNING, Voucher.PRODUTO_SMIME,
                Voucher.PRODUTO_JRE, Voucher.PRODUTO_SSL_MDC_DOMINIO, Voucher.PRODUTO_SSL_EV_MDC_DOMINIO,
                Voucher.PRODUTO_SSL_SAN_FQDN
            )
            self._tem_contrato_ssl = any(line.product.attr.ssl_code.option in codigos
                                         for line in self.all_lines())

        return self._tem_contrato_ssl

    def tem_contrato_siteseguro(self):
        if self._tem_contrato_siteseguro is None:
            from ecommerce.certificados.models import Voucher
            self._tem_contrato_siteseguro = any(line.product.attr.ssl_code.option == Voucher.PRODUTO_SITE_SEGURO
                                                for line in self.all_lines())
        return self._tem_contrato_siteseguro

    def tem_contrato_sitemonitorado(self):
        if self._tem_contrato_sitemonitorado is None:
            from ecommerce.certificados.models import Voucher
            self._tem_contrato_sitemonitorado = any(line.product.attr.ssl_code.option == Voucher.PRODUTO_SITE_MONITORADO
                                                    for line in self.all_lines())
        return self._tem_contrato_sitemonitorado

    def tem_contrato_pki(self):
        if self._tem_contrato_pki is None:
            from ecommerce.certificados.models import Voucher
            self._tem_contrato_pki = any(line.product.attr.ssl_code.option == Voucher.PRODUTO_PKI
                                         for line in self.all_lines())
        return self._tem_contrato_pki

from oscar.apps.basket.models import *