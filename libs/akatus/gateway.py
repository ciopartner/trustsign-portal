# -*- coding: utf-8 -*-

import requests
from lxml import etree
from lxml.etree import tostring
from lxml.builder import E, ElementMaker

class Akatus(object):
    """
    This class is responsible for the integration to Akatus.
    This file is not intended to depend on Django, Oscar or Mezzanine
    Everything in this class where we put Gateway, it should be read as 'Intermediador Financeiro'
    """

    def __init__(self, *args, **kwargs):
        self.URL = kwargs.get('AKATUS_URL')
        self.API_KEY = kwargs.get('AKATUS_API_KEY')
        self.USER = kwargs.get('AKATUS_USER')

    def post_credit_card(self, options):
        """
        Efetua o POST de uma solicitação de pagamento via cartão de crédito
        """
        carrinho = {
            'recebedor': {
                'api_key': self.API_KEY,
                'email': self.USER,
            },

            'pagador': {
	            'nome': 'Jose Antonio',
	            'email': 'ze@antonio.com.br',
	            'enderecos': {
    	            'endereco': {
    	                'tipo': 'entrega',
    	                'logradouro': 'Rua Labib Marrar',
    	                'numero': '129',
    	                'bairro': 'Jardim Santa Cruz',
    	                'cidade': 'São Paulo',
    	                'estado': 'SP',
    	                'pais': 'BRA',
    	                'cep': '04182-040',
                    },
                },
               'telefones': {
                    'telefone': {
                        'tipo': 'residencial',
                        'numero': '1433019799',
                    },
                }
            },
            'transacao': {
                'numero': 'NUMERO_DO_CARTAO_DE_CREDITO',
                'parcelas': '1',
                'codigo_de_seguranca': '643',
                'expiracao': '03/2015',
                'desconto': '20.00',
                'peso': '17.00',
                'frete': '32.90',
                'moeda': 'BRL',
                'referencia': 'abc1234',
                'meio_de_pagamento': 'cartao_master',
                'portador': {
                    'nome': 'NOME IMPRESSO NO CARTAO',
                    'cpf': 'CPF DO PORTADOR',
                    'telefone': 'TELEFONE DO PORTADOR',
                }
            },
    	    'produtos': {
                'produto': {
                    'codigo': 'UFC1403',
                    'descricao': 'Luva de box com ferradura dentro',
                    'quantidade': '1',
                    'preco': '148.99',
                    'peso': '0',
                    'frete': '0',
                    'desconto': '0',
                }
            }
        }
        result = requests.post(self.URL+'/'+METHOD, {'PedidoXML': xml_str})
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

