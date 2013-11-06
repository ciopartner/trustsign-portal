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
        'carrinho': '/api/v1/carrinho.json',
    }

    def __init__(self, *args, **kwargs):
        self.URL = kwargs.get('AKATUS_URL')
        self.API_KEY = kwargs.get('AKATUS_API_KEY')
        self.USER = kwargs.get('AKATUS_USER')

    def get_method_url(self, method):
        return '{}/{}'.format(self.URL, self.METHODS[method])

    def call_server(self, method, data):
        return requests.post(self.get_method_url(method), data)

    def post_credit_card(self, options):
        """
        Efetua o POST de uma solicitação de pagamento via cartão de crédito
        """
        carrinho = {
            'recebedor': {
                'api_key': self.API_KEY,
                'email': self.USER,
            },

            'pagador': options['pegador'],
            'transacao': options['transacao'],
            'produtos': options['produtos']
        }

        result = self.call_server('carrinho', json.dumps(carrinho))
        #import ipdb; ipdb.set_trace()
        return result

    def post_debit_card(self, options):
        """
        Efetua o POST de uma solicitação de pagamento via cartão de crédito
        """
        carrinho = {
            'recebedor': {
                'api_key': '',
                'email': ''
            },
        }

    def post_boleto(self, options):
        """
        Efetua o POST de uma solicitação de pagamento via cartão de crédito
        """
        carrinho = {
            'recebedor': {
                'api_key': '',
                'email': ''
            },
        }

    def get_installments(self, amount, method):
        pass

