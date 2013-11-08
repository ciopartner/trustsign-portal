# -*- coding: utf-8 -*-
from django.template import Context
from django.template.loader import get_template
from oscar.apps.payment.exceptions import GatewayError

import requests
import logging
from ecommerce.website.utils import xml_to_dict

log = logging.getLogger('libs.akatus.gateway')


class Akatus(object):
    """
    This class is responsible for the integration to Akatus.
    This file is not intended to depend on Django, Oscar or Mezzanine
    Everything in this class where we put Gateway, it should be read as 'Intermediador Financeiro'
    """

    METHODS = {
        'carrinho': 'api/v1/carrinho.xml',
        'installments': 'api/v1/parcelamento/simulacao.xml',
    }

    def __init__(self, *args, **kwargs):
        self.URL = kwargs.get('AKATUS_URL')
        self.API_KEY = kwargs.get('AKATUS_API_KEY')
        self.USER = kwargs.get('AKATUS_USER')

    def get_method_url(self, method):
        return '{}/{}'.format(self.URL, self.METHODS[method])

    def call_server_post(self, method, data):
        """
        Realiza um POST no servidor passando a data (uma string XML) e retornando um dict com os dados da resposta
        """
        response = requests.post(self.get_method_url(method), data.encode('utf-8'))

        if response.status_code != 200:
            log.warning('Ocorreu um erro durante a chamada do método: {}\ndata: {} \nresponse: {}\n'.format(method, data, response.text.encode('utf8')))
            raise GatewayError('Ocorreu um erro durante a chamada do gateway')

        log.info('URL: {}\nrequest:\n{}\nresponse:\n{}\n'.format(self.get_method_url(method), data.encode('utf8'), response.text.encode('utf8')))

        return xml_to_dict(response.text.encode('utf-8'))

    def call_server_get(self, method, data):
        response = requests.get(self.get_method_url(method), params=data)

        if response.status_code != 200:
            log.warning('Ocorreu um erro durante a chamada do método: {}\ndata: {} \nresponse: {}\n'.format(method, data, response.text))
            raise GatewayError('Ocorreu um erro durante a chamada do gateway')

        return response

    def post_payment(self, options):
        """
        Efetua o POST de uma solicitação de pagamento via cartão de crédito, débito ou boleto
        """
        context = {
            'recebedor': {
                'api_key': self.API_KEY,
                'email': self.USER,
            },

            'pagador': options['pagador'],
            'transacao': options['transacao'],
            'produtos': options['produtos']
        }

        template = get_template('checkout/akatus/carrinho.xml')

        result = self.call_server_post('carrinho', template.render(Context(context)))
        #import ipdb; ipdb.set_trace()
        return result['resposta']

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

