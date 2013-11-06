# -*- coding: utf-8 -*-
import json

import requests


class Akatus(object):
    """
    This class is responsible for the integration to Akatus.
    This file is not intended to depend on Django, Oscar or Mezzanine
    Everything in this class where we put Gateway, it should be read as 'Intermediador Financeiro'
    """

    METHODS = {
        'carrinho': 'api/v1/carrinho.json',
        'installments': 'api/v1/parcelamento/simulacao.json',
    }

    def __init__(self, *args, **kwargs):
        self.URL = kwargs.get('AKATUS_URL')
        self.API_KEY = kwargs.get('AKATUS_API_KEY')
        self.USER = kwargs.get('AKATUS_USER')

    def get_method_url(self, method):
        return '{}/{}'.format(self.URL, self.METHODS[method])

    def call_server_post(self, method, data):
        return requests.post(self.get_method_url(method), data)

    def call_server_get(self, method, data):
        return requests.get(self.get_method_url(method), params=data)

    def post_payment(self, options):
        """
        Efetua o POST de uma solicitação de pagamento via cartão de crédito, débito ou boleto
        """
        carrinho = {
            'recebedor': {
                'api_key': self.API_KEY,
                'email': self.USER,
            },

            'pagador': options['pagador'],
            'transacao': options['transacao'],
            'produtos': options['produtos']
        }

        result = self.call_server_post('carrinho', json.dumps(carrinho))
        #import ipdb; ipdb.set_trace()
        return result

    def get_installments(self, amount, card='cartao_visa'):
        """
        Get the installments amount for the given card.
        payment_method = cartao_visa, cartao_master, cartao_amex, cartao_elo e cartao_dinners
        """
        parameters = {
            'email': self.USER,
            'api_key': self.API_KEY,
            'amount': unicode(amount).replace('.', '').replace(',', ''),
            'payment_method': card,
        }

        result = self.call_server_get('installments', parameters)
        return result

