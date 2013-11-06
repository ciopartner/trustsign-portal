# -*- coding: utf-8 -*-
import datetime

from django.conf import settings
from ecommerce.website.utils import formata_cnpj
from gateway import *
from oscar.apps.payment.exceptions import UnableToTakePayment, InvalidGatewayRequestError

class Facade(object):
    """
    This class aims to comunicate with the gateway using the gateway.py.
    It is dependent on Django
    """

    def __init__(self, *args, **kwargs):
        self.AKATUS_URL = settings.AKATUS_URL
        self.AKATUS_EMAIL = settings.AKATUS_EMAIL
        self.AKATUS_API_KEY = settings.AKATUS_API_KEY
        self.gateway = Akatus(AKATUS_URL=self.AKATUS_URL,
                              AKATUS_USER=self.AKATUS_EMAIL,
                              AKATUS_API_KEY=self.AKATUS_API_KEY)

    def post_creditcard_payment(self, request, order_number, total_incl_tax):
        """
        This method is responsible for taking care of the payment.
        """
        ip = request.META['REMOTE_ADDR']

        options = {}

        # Customer data:
        options['nome'] = ''
        options['email'] = ''
        options['enderecos'] = [
            {
                'endereco': {
                    'tipo': 'entrega',
                    'logradouro': 'Rua Labib Marrar',
                    'numero': '129',
                    'bairro': 'Jardim Santa Cruz',
                    'cidade': 'São Paulo',
                    'estado': 'SP',
                    'pais': 'BRA',
                    'cep': '04182-040',
                }
            }
        ]

        options['DataCadastro'] = request.user.date_joined.strftime('%d/%m/%Y')
        options['Sobrenome'] = ''
        options['RazaoSocial'] = request.user.get_profile().cliente_razaosocial
        options['Genero'] = 'J'
        options['CpfCnpj'] = request.user.get_profile().cliente_cnpj
        options['NascAbertura'] = ''
        options['Login'] = formata_cnpj(request.user.get_profile().cliente_cnpj)
        options['Moeda'] = 'BRL'
        options['Idioma'] = 'PT-BR'
        options['IpCadastro'] = ip
        options['Notas'] = ''

        # Customer billing address
        options['Endereco'] = request.user.get_profile().cliente_logradouro
        options['Numero'] = request.user.get_profile().cliente_numero
        options['Complemento'] = request.user.get_profile().cliente_complemento
        options['Bairro'] = request.user.get_profile().cliente_bairro
        options['Cidade'] = request.user.get_profile().cliente_cidade
        options['UF'] = request.user.get_profile().cliente_uf
        options['CEP'] = request.user.get_profile().cliente_cep
        options['Pais'] = 'Brasil'
        options['DDD'] = ''
        options['Telefone'] = request.user.get_profile().callback_telefone_principal
        options['Tipo'] = 'Comercial'

        # Customer e-mail
        options['Email'] = request.user.get_profile().callback_email_corporativo

        # Order data
        options['LojaCanal'] = 'WEB'
        options['MeiosdePagamento'] = request.POST.get('MD_MeioPagto')
        options['PedidoCodigo'] = unicode(order_number)
        options['PedidoNumeroLoja'] = unicode(order_number)
        options['PedidoEmissao'] = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        options['PedidoVencimento'] = (datetime.datetime.now() +
                                          datetime.timedelta(days=7)).strftime('%d/%m/%Y %H:%M:%S')
        options['PedidoExpiracao'] = (datetime.datetime.now() +
                                         datetime.timedelta(days=7)).strftime('%d/%m/%Y %H:%M:%S')
        options['PedidoRecorrente'] = 'N'
        options['PedidoValor'] = request.basket.total_incl_tax.to_eng_string().replace('.','')
        options['PedidoValorSemJuros'] = request.basket.total_incl_tax.to_eng_string().replace('.','')
        options['PedidoMulta'] = ''
        options['PedidoJuros'] = ''
        # Todo: validar se este num_itens é itens total ou itens diferentes
        options['PedidoItens'] = unicode(request.basket.num_items)
        options['PedidoParcelas'] = request.POST.get('MD_FormaPagto')
        options['PedidoValorParcelas'] = request.POST.get('MD_ValorParcela')
        # 1 - Administradora; 2 - Loja
        options['PedidoFinanciador'] = '1'
        options['PedidoInstrucoes'] = u'Sr Caixa: não receber após o vencimento.'
        options['PortadorCartao'] = ''
        options['PortadorValidade'] = ''
        options['PortadorCVV'] = ''
        options['PortadorNome'] = ''

        gateway.post_payment(options)

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

