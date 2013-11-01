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
    URL = 'http://moedadigital.net/Gateway.asmx'
    USER = 'reichert@ciopartner.com.br'
    PASSWORD = 'reic2013'
    TOKEN = 'b5529d3d-e64d-4bc3-be77-625349011828'
    APPLICATION = 'ReichertTESTE'

    def get_payment_html(self, request, amount):
        """
        This method requests CobreBem Approval for Credit Card.
        You must call the capture method to confirm the transaction.
        """
        ip = request.META['REMOTE_ADDR']
        gateway = MoedaDigital()

        if amount == 0:
            raise UnableToTakePayment("Order amount must be non-zero")
        response = gateway.get_installments_html(amount)
        if response:
            return response
        raise UnableToTakePayment("Erro na comunicação com o gateway de pagamento.")

    def post_payment(self, request, order_number, total_incl_tax):
        """
        This method is responsible for taking care of the payment.
        """
        ip = request.META['REMOTE_ADDR']
        gateway = MoedaDigital()

        parameters = {}
        parameters['LojaChaveAcesso'] = self.TOKEN
        parameters['LojaApp'] = self.APPLICATION

        # Customer data:
        parameters['DataCadastro'] = request.user.date_joined.strftime('%d/%m/%Y')
        parameters['Nome'] = ''
        parameters['Sobrenome'] = ''
        parameters['RazaoSocial'] = request.user.get_profile().cliente_razaosocial
        parameters['Genero'] = 'J'
        parameters['CpfCnpj'] = request.user.get_profile().cliente_cnpj
        parameters['NascAbertura'] = ''
        parameters['Login'] = formata_cnpj(request.user.get_profile().cliente_cnpj)
        parameters['Moeda'] = 'BRL'
        parameters['Idioma'] = 'PT-BR'
        parameters['IpCadastro'] = ip
        parameters['Notas'] = ''

        # Customer billing address
        parameters['Endereco'] = request.user.get_profile().cliente_logradouro
        parameters['Numero'] = request.user.get_profile().cliente_numero
        parameters['Complemento'] = request.user.get_profile().cliente_complemento
        parameters['Bairro'] = request.user.get_profile().cliente_bairro
        parameters['Cidade'] = request.user.get_profile().cliente_cidade
        parameters['UF'] = request.user.get_profile().cliente_uf
        parameters['CEP'] = request.user.get_profile().cliente_cep
        parameters['Pais'] = 'Brasil'
        parameters['DDD'] = ''
        parameters['Telefone'] = request.user.get_profile().callback_telefone_principal
        parameters['Tipo'] = 'Comercial'

        # Customer e-mail
        parameters['Email'] = request.user.get_profile().callback_email_corporativo

        # Order data
        parameters['LojaCanal'] = 'WEB'
        parameters['MeiosdePagamento'] = request.POST.get('MD_MeioPagto')
        parameters['PedidoCodigo'] = unicode(order_number)
        parameters['PedidoNumeroLoja'] = unicode(order_number)
        parameters['PedidoEmissao'] = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        parameters['PedidoVencimento'] = (datetime.datetime.now() +
                                          datetime.timedelta(days=7)).strftime('%d/%m/%Y %H:%M:%S')
        parameters['PedidoExpiracao'] = (datetime.datetime.now() +
                                         datetime.timedelta(days=7)).strftime('%d/%m/%Y %H:%M:%S')
        parameters['PedidoRecorrente'] = 'N'
        parameters['PedidoValor'] = request.basket.total_incl_tax.to_eng_string().replace('.','')
        parameters['PedidoValorSemJuros'] = request.basket.total_incl_tax.to_eng_string().replace('.','')
        parameters['PedidoMulta'] = ''
        parameters['PedidoJuros'] = ''
        # Todo: validar se este num_itens é itens total ou itens diferentes
        parameters['PedidoItens'] = unicode(request.basket.num_items)
        parameters['PedidoParcelas'] = request.POST.get('MD_FormaPagto')
        parameters['PedidoValorParcelas'] = request.POST.get('MD_ValorParcela')
        # 1 - Administradora; 2 - Loja
        parameters['PedidoFinanciador'] = '1'
        parameters['PedidoInstrucoes'] = u'Sr Caixa: não receber após o vencimento.'
        parameters['PortadorCartao'] = ''
        parameters['PortadorValidade'] = ''
        parameters['PortadorCVV'] = ''
        parameters['PortadorNome'] = ''

        gateway.post_payment(parameters)
