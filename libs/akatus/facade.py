# -*- coding: utf-8 -*-
from django.conf import settings
from oscar.apps.payment import bankcards
from ecommerce.website.utils import limpa_telefone
from gateway import *
from oscar.apps.payment.exceptions import UnableToTakePayment, InvalidGatewayRequestError

class Facade(object):
    """
    This class aims to comunicate with the gateway using the gateway.py.
    It is dependent on Django
    """

    def __init__(self, *args, **kwargs):
        self.AKATUS_URL = settings.AKATUS_URL()
        self.AKATUS_EMAIL = settings.AKATUS_EMAIL
        self.AKATUS_API_KEY = settings.AKATUS_API_KEY
        self.gateway = Akatus(AKATUS_URL=self.AKATUS_URL,
                              AKATUS_USER=self.AKATUS_EMAIL,
                              AKATUS_API_KEY=self.AKATUS_API_KEY)

    def post_creditcard_payment(self, request, order, bankcard):
        """
        This method is responsible for taking care of the payment.
        """
        options = {
            'pagador': self.get_dados_pagador(request.user),
            'transacao': self.get_dados_transacao_credito(order, bankcard),
            'produtos': self.get_dados_produtos(order.lines.all())
        }

        self.gateway.post_credit_card(options)

    def get_payment_installments(self, request, amount):
        """
        This method requests Akatus webservice for installments for Credit Card.
        You must call the capture method to confirm the transaction.
        """
        ip = request.META['REMOTE_ADDR']
        gateway = Akatus()

        if amount == 0:
            raise UnableToTakePayment("Order amount must be non-zero")
        response = gateway.get_installments(amount, 'VISA')
        if response:
            return response
        raise UnableToTakePayment("Erro na comunicação com o gateway de pagamento.")

    def get_dados_pagador(self, user):
        profile = user.get_profile()

        return {
            'nome': user.get_full_name(),
            'email': user.email,
            'enderecos': [{
                'tipo': 'comercial',
                'logradouro': profile.cliente_logradouro,
                'numero': profile.cliente_numero,
                'bairro': profile.cliente_bairro,
                'cidade': profile.cliente_cidade,
                'estado': profile.cliente_uf,
                'pais': 'BRA',
                'cep': profile.cliente_cep.remove('-'),
            }],
            'telefones': [{
                'tipo': 'comercial',
                'numero': limpa_telefone(profile.callback_telefone_principal)
            }],
        }

    def get_dados_transacao_credito(self, order, bankcard):
        tipo_cartao = bankcard.card_type
        if tipo_cartao in (bankcards.VISA, bankcards.VISA_ELECTRON):
            meio_de_pagamento = 'cartao_visa'
        elif tipo_cartao == bankcards.MASTERCARD:
            meio_de_pagamento = 'cartao_master'
        elif tipo_cartao == bankcards.AMEX:
            meio_de_pagamento = 'cartao_amex'
        elif tipo_cartao == bankcards.DINERS_CLUB:
            meio_de_pagamento = 'cartao_dinners'
        else:
            raise UnableToTakePayment('Bandeira do cartão inválida')

        return {
            'numero': bankcard.number.remove('-'),
            'parcelas': '1',
            'codigo_de_seguranca': bankcard.cvv,
            'expiracao': bankcard.expiry_month(),
            'desconto': '0.00',
            'peso': '0.00',
            'frete': '0.00',
            'moeda': 'BRL',
            'referencia': order.number,
            'meio_de_pagamento': meio_de_pagamento,

            'portador': {
                'nome': bankcard.name,
                'cpf': bankcard.cpf,
                'telefone': bankcard.telefone_portador,
            }
        }

    def get_dados_transacao_debito(self, order, bankcard):
        """
        Compila os dados de cartão de débito
        meio_de_pagamento = tef_itau/tef_bradesco/tef_bb
        """
        bank_name = bankcard.bank_name
        if bank_name == 'BRADESCO':
            meio_de_pagamento = 'cartao_master'
        elif bank_name == 'ITAU':
            meio_de_pagamento = 'tef_itau'
        elif bank_name == 'BB':
            meio_de_pagamento = 'tef_bb'
        else:
            raise UnableToTakePayment('Banco {} Inválido'.format(bank_name))

        return {
            'desconto': '0.00',
            'peso': '0.00',
            'frete': '0.00',
            'moeda': 'BRL',
            'referencia': order.number,
            'meio_de_pagamento': meio_de_pagamento,
        }

    def get_dados_transacao_boleto(self, order):
        """
        Compila os dados de cartão de débito
        meio_de_pagamento = tef_itau/tef_bradesco/tef_bb
        """
        meio_de_pagamento = 'boleto'
        return {
            'desconto': '0.00',
            'peso': '0.00',
            'frete': '0.00',
            'moeda': 'BRL',
            'referencia': order.number,
            'meio_de_pagamento': meio_de_pagamento,
        }

    def get_dados_produtos(self, lines):

        return [{
            'codigo': line.product.upc,
            'descricao': line.product.title,
            'quantidade': line.quantity,
            'preco': str(line.line_price_incl_tax),
            'peso': '0',
            'frete': '0',
            'desconto': '0',
        } for line in lines]
