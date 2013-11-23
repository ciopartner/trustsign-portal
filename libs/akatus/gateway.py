# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from decimal import Decimal
import json
from django.conf import settings
from django.template import Context
from django.template.loader import get_template
from django.utils.encoding import smart_unicode
from oscar.apps.payment.exceptions import GatewayError

import requests
import logging
import re
from ecommerce.website.utils import xml_to_dict

log = logging.getLogger('libs.akatus.gateway')


class Akatus(object):
    """
    This class is responsible for the integration to Akatus.
    This file is not intended to depend on Django, Oscar or Mezzanine
    Everything in this class where we put Gateway, it should be read as 'Intermediador Financeiro'
    """

    METHODS = {
        'carrinho': ('api/v1/carrinho.xml', 'POST'),
        'installments': ('api/v1/parcelamento/simulacao.json', 'GET'),
    }

    def __init__(self, *args, **kwargs):
        self.URL = kwargs.get('AKATUS_URL')
        self.API_KEY = kwargs.get('AKATUS_API_KEY')
        self.USER = kwargs.get('AKATUS_USER')

    def get_method_details(self, method):
        url, tipo = self.METHODS[method]
        return '{}/{}'.format(self.URL, url), tipo

    def call_server(self, method, data):
        url, tipo = self.get_method_details(method)
        log.debug('Request via {} para {}\nDados do Request: {}'.format(tipo, url, smart_unicode(data)))
        if tipo == 'GET':
            response = requests.get(url, params=data)
        elif tipo == 'POST':
            response = requests.post(url, data=data)
        else:
            log.error('URLs do Akatus.METHODS configurado errado')
            raise GatewayError('Ocorreu um erro durante a chamada do gateway')

        resposta = response.text.encode('utf-8')
        log.debug('\nDados do Response: {}'.format(smart_unicode(resposta)))

        if response.status_code != 200:
            log.error('URL chamada: {}'.format(response.request_url))
            log.error('HTTP Response retornado da Akatus: {}'.format(response.status_code))
            log.error('Dados enviados para a Akatus via {}: {}'.format(method, smart_unicode(data)))
            log.error('Dados retornados da Akatus via {}: {}'.format(method, smart_unicode(resposta)))
            raise GatewayError('Ocorreu um erro durante a chamada do gateway')

        if url.endswith('.xml'):
            return xml_to_dict(resposta)
        elif url.endswith('.json'):
            return json.loads(resposta)
        else:
            log.warning('URLs do Akatus.METHODS configurado errado')
            raise GatewayError('Ocorreu um erro durante a chamada do gateway')

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

        data = template.render(Context(context)).encode('utf-8')

        result = self.call_server('carrinho', data)
        return result['resposta']

    def get_installments(self, amount, card='cartao_visa'):
        """
        Get the installments amount for the given card.
        payment_method = cartao_visa, cartao_master, cartao_amex, cartao_elo e cartao_dinners
        """

        def limpa_amount(amt):
            """
            A Akatus assume que o amount está sem pontuação e com duas casas decimais: R$ 14.332,50 == 1433250
            """
            return re.sub('[.,]', '', unicode(amt.quantize(Decimal('0.01'))))

        parameters = {
            'email': self.USER,
            'api_key': self.API_KEY,
            'amount': unicode(amount.quantize(Decimal('0.01'))),
            'payment_method': card,
        }

        result = self.call_server('installments', parameters)

        # Filtra a quantidade de parcelas
        result['resposta']['parcelas'] = result['resposta']['parcelas'][:getattr(settings, 'AKATUS_MAX_INSTALLMENTS', 3)]

        return result['resposta']