# -*- coding: utf-8 -*-

import requests
from lxml import etree
from lxml.etree import tostring
from lxml.builder import E, ElementMaker
import suds

class MoedaDigital(object):
    """
    This class is responsible for the integration to Moeda Digital.
    This file is not intended to depend on Django, Oscar or Mezzanine
    Everything in this class where we put Gateway, it should be read as 'Intermediador Financeiro'
    """

    URL = 'http://www.moedadigital.net/Gateway.asmx'
    USER = 'reichert@ciopartner.com.br'
    PASSWORD = 'reic2013'
    TOKEN = 'b5529d3d-e64d-4bc3-be77-625349011828'
    APPLICATION = 'ReichertTESTE'

    def get_payment_methods(self, payment_methods='Credito Debito Boleto'):
        """
        This method is responsible for retrieving the payment methods from the gateway
        """
        METHOD = 'ConsultaMeiosDePagamento'
        parameters = {}
        parameters['Loja'] = self.TOKEN
        parameters['Aplicacao'] = self.APPLICATION
        parameters['Meios'] = payment_methods

        # Post the query
        result = requests.post(self.URL+'/'+METHOD, parameters)
        return result

    def get_parcelas(self, amount):
        METHOD = 'ConsultaParcelas'
        parameters = {}
        parameters['Loja'] = self.TOKEN
        parameters['Aplicacao'] = self.APPLICATION

        # The amount must be without decimal separator
        parameters['Valor'] = unicode(amount).replace('.','').replace(',','')

        # Post the query
        result = requests.post(self.URL+'/'+METHOD, parameters)
        return result

    def get_installments_html(self, amount, payment_methods='Credito Debito Boleto'):
        """
        This method is responsible for getting the full HTML used to show the payment conditions like:
        - payment method;
        - installments and values;
        """
        METHOD = 'ConsultaMeiosDePagamentoHTMLv2'
        parameters = {}
        parameters['Loja'] = self.TOKEN
        parameters['Aplicacao'] = self.APPLICATION
        parameters['Meios'] = payment_methods
        parameters['Idioma'] = 'PT-BR'

        # The amount must be without decimal separator
        parameters['Valor'] = unicode(amount).replace('.','').replace(',','')

        # Post the query
        response_gateway = requests.post(self.URL+'/'+METHOD, parameters)
        response_etree = etree.fromstring(response_gateway.content)
        response_html = response_etree.text
        #doc = ET.fromstring(response.encode("utf-8"))
        return response_html

    def post_payment(self, parameters):
        """
        This method is responsible for taking the payment.
        """
        METHOD = 'IniciarPagamentoXML'

        Cliente = E.Cliente(
            E.DataCadastro(parameters.get('DataCadastro')),
            E.Nome(parameters.get('Nome')),
            E.Sobrenome(parameters.get('Sobrenome')),
            E.RazaoSocial(parameters.get('RazaoSocial')),
            E.Genero(parameters.get('Genero')),
            E.CpfCnpj(parameters.get('CpfCnpj')),
            E.NascAbertura(parameters.get('NascAbertura')),
            E.Login(parameters.get('Login')),
            E.Moeda(parameters.get('Moeda')),
            E.Idioma(parameters.get('Idioma')),
            E.IpCadastro(parameters.get('IpCadastro')),
            E.Notas(parameters.get('Notas'))
        )

        Endereco1 = E.Endereco1(
            E.Endereco(parameters.get('Endereco')),
            E.Numero(parameters.get('Numero')),
            E.Complemento(parameters.get('Complemento')),
            E.Bairro(parameters.get('Bairro')),
            E.Cidade(parameters.get('Cidade')),
            E.UF(parameters.get('UF')),
            E.CEP(parameters.get('CEP')),
            E.Pais(parameters.get('Pais')),
            E.DDD(parameters.get('DDD')),
            E.Telefone(parameters.get('Telefone')),
            E.Tipo(parameters.get('Tipo'))
        )

        Email1 = E.Email1(
            E.Email(parameters.get('Email'))
        )

        E2 = ElementMaker (
            #namespace='http://www.w3.org/2001/XMLSchema-instance',
            nsmap={'xsi': 'http://www.w3.org/2001/XMLSchema-instance', 'xsd':'http://www.w3.org/2001/XMLSchema'},
        )

        clsPedido = E2.clsPedido(
            E.LojaChaveAcesso(parameters.get('LojaChaveAcesso')),
            E.LojaApp(parameters.get('LojaApp')),

            E.LojaCanal(parameters.get('LojaCanal')),
            E.MeiosdePagamento(parameters.get('MeiosdePagamento')),
            E.PedidoCodigo(parameters.get('PedidoCodigo')),
            E.PedidoNumeroLoja(parameters.get('PedidoNumeroLoja')),
            E.PedidoEmissao(parameters.get('PedidoEmissao')),
            E.PedidoVencimento(parameters.get('PedidoVencimento')),
            E.PedidoExpiracao(parameters.get('PedidoExpiracao')),
            E.PedidoRecorrente(parameters.get('PedidoRecorrente')),
            E.PedidoValor(parameters.get('PedidoValor')),
            E.PedidoValorSemJuros(parameters.get('PedidoValorSemJuros')),
            E.PedidoMulta(parameters.get('PedidoMulta')),
            E.PedidoJuros(parameters.get('PedidoJuros')),
            E.PedidoItens(parameters.get('PedidoItens')),
            E.PedidoParcelas(parameters.get('PedidoParcelas')),
            E.PedidoValorParcelas(parameters.get('PedidoValorParcelas')),
            E.PedidoFinanciador(parameters.get('PedidoFinanciador')),
            E.PedidoInstrucoes(parameters.get('PedidoInstrucoes')),
            #E.PortadorCartao(parameters.get('PortadorCartao')),
            #E.PortadorValidade(parameters.get('PortadorValidade')),
            #E.PortadorCVV(parameters.get('PortadorCVV')),
            #E.PortadorNome(parameters.get('PortadorNome')),

            Cliente,
            Endereco1,
            Email1
        )

        #Cliente = {
        #    'DataCadastro': parameters.get('DataCadastro'),
        #    'Nome': parameters.get('Nome'),
        #    'Sobrenome': parameters.get('Sobrenome'),
        #    'RazaoSocial': parameters.get('RazaoSocial'),
        #    'Genero': parameters.get('Genero'),
        #    'CpfCnpj': parameters.get('CpfCnpj'),
        #    'NascAbertura': parameters.get('NascAbertura'),
        #    'Login': parameters.get('Login'),
        #    'Moeda': parameters.get('Moeda'),
        #    'Idioma': parameters.get('Idioma'),
        #    'IpCadastro': parameters.get('IpCadastro'),
        #    'Notas': parameters.get('Notas'),
        #}
        #
        #Endereco1 = {
        #    'Endereco': parameters.get('Endereco'),
        #    'Numero': parameters.get('Numero'),
        #    'Complemento': parameters.get('Complemento'),
        #    'Bairro': parameters.get('Bairro'),
        #    'Cidade': parameters.get('Cidade'),
        #    'UF': parameters.get('UF'),
        #    'CEP': parameters.get('CEP'),
        #    'Pais': parameters.get('Pais'),
        #    'DDD': parameters.get('DDD'),
        #    'Telefone': parameters.get('Telefone'),
        #    'Tipo': parameters.get('Tipo'),
        #}
        #
        #Email1 = {
        #    'Email': parameters.get('Email'),
        #}
        #
        #clsPedido = {
        #    'LojaChaveAcesso': parameters.get('LojaChaveAcesso'),
        #    'LojaApp': parameters.get('LojaApp'),
        #
        #    'LojaCanal': parameters.get('LojaCanal'),
        #    'MeiosdePagamento': parameters.get('MeiosdePagamento'),
        #    'PedidoCodigo': parameters.get('PedidoCodigo'),
        #    'PedidoNumeroLoja': parameters.get('PedidoNumeroLoja'),
        #    'PedidoEmissao': parameters.get('PedidoEmissao'),
        #    'PedidoVencimento': parameters.get('PedidoVencimento'),
        #    'PedidoExpiracao': parameters.get('PedidoExpiracao'),
        #    'PedidoRecorrente': parameters.get('PedidoRecorrente'),
        #    'PedidoValor': parameters.get('PedidoValor'),
        #    'PedidoValorSemJuros': parameters.get('PedidoValorSemJuros'),
        #    'PedidoMulta': parameters.get('PedidoMulta'),
        #    'PedidoJuros': parameters.get('PedidoJuros'),
        #    'PedidoItens': parameters.get('PedidoItens'),
        #    'PedidoParcelas': parameters.get('PedidoParcelas'),
        #    'PedidoValorParcelas': parameters.get('PedidoValorParcelas'),
        #    'PedidoFinanciador': parameters.get('PedidoFinanciador'),
        #    'PedidoInstrucoes': parameters.get('PedidoInstrucoes'),
        #    'PortadorCartao': parameters.get('PortadorCartao'),
        #    'PortadorValidade': parameters.get('PortadorValidade'),
        #    'PortadorCVV': parameters.get('PortadorCVV'),
        #    'PortadorNome': parameters.get('PortadorNome'),
        #
        #    'Cliente': Cliente,
        #    'Endereco1': Endereco1,
        #    'Email1': Email1,
        #}

        # Post the query
        xml_str = tostring(clsPedido,
                           pretty_print=False,
                           xml_declaration=True,
                           encoding='utf-8').replace("\'", "\"")
        #result = requests.post(self.URL+'/'+METHOD, {'PedidoXML': xml_str})
        result = requests.get(self.URL+'/'+METHOD + '?PedidoXML='+xml_str)
        import ipdb; ipdb.set_trace()
        return result