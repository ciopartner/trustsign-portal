# coding=utf-8
#from django.conf import settings
from __future__ import unicode_literals
import requests
import json
from logging import getLogger

log = getLogger('libs.crm')


class ClienteCRM(object):

    def __init__(self):

        self.cnpj = None
        self.razaosocial = None
        self.logradouro = None
        self.numero = None
        self.complemento = None
        self.bairro = None
        self.cidade = None
        self.estado = None
        self.pais = None
        self.cep = None
        self.sem_atividade = None


class OportunidadeCRM(object):
    def __init__(self):
        self.account_id = None
        self.name = 'Oportunidade via e-commerce'
        self.numero_pedido = None
        self.data_pedido = None
        self.valor_total = None

        # cartão de credito
        self.pag_credito_titular = None
        self.pag_credito_vencimento = None
        self.pag_credito_bandeira = None
        self.pag_credito_transacao_id = None
        self.pag_credito_ultimos_digitos = None

        #cartão de débito
        self.pag_debito_titular = None
        self.pag_debito_vencimento = None
        self.pag_debito_bandeira = None
        self.pag_debito_transacao_id = None
        self.pag_debito_ultimos_digitos = None

        #boleto
        #TODO: dados boleto em oportunidade

    def is_credito(self):
        return self.pag_credito_ultimos_digitos is not None

    def is_debito(self):
        return self.pag_debito_ultimos_digitos is not None

    def is_boleto(self):
        return False


class ProdutoCRM(object):

    def __init__(self):
        self.account_id = None
        self.opportunity_id = None
        self.codigo = None
        self.preco_venda = None,
        self.quantidade = None,


class CRMClient(object):

    def __init__(self):
        self.session_id = None

    class CRMError(Exception):
        """
        Ocorreu um erro na integração com o CRM
        """
        pass

    def call_crm(self, method, rest_data, url='http://dev2.lampadaglobal.com/projects/trustsign/service/v4_1/rest.php',
                 input_type='json', response_type='json'):
        """
        Todos os métodos usam este para executar a chamada ao CRM
        """

        if not self.session_id and method != 'login':
            raise self.CRMError('Desconectado')

        response = requests.post(url, {
            'method': method,
            'input_type': input_type,
            'response_type': response_type,
            'rest_data': json.dumps(rest_data)
        })

        return response.json()

    def login(self, canal="Portal"):
        """
        Inicia a sessão
        """

        response_data = self.call_crm('login', [
            {
                'user_name': 'ceo',  # settings.CRM_USERNAME,
                'password': '26442effb42e24d42f179f343c89e419',  # settings.CRM_PASSWORD_HASH,
            },
            canal
        ])
        if 'id' not in response_data:
            log.warning('Erro durante a chamada do metodo login do crm: %s' % response_data)
            raise self.CRMError('Erro durante a chamada do método login do crm')
        self.session_id = response_data['id']
        return response_data['id']

    def logout(self):
        """
        Encerra a sessão
        """
        self.call_crm('logout', [self.session_id])
        self.session_id = None

    def get_account(self, cnpj):
        """
        Retorna dados de uma Account
        """
        response_data = self.call_crm('get_entry_list', [
            self.session_id,
            'Accounts',
            'accounts_cstm.corporate_tax_registry_c = \'%s\'' % cnpj,
            '',
            0,
            ['id', 'name'],
            [],
            1,
            0,
            False
        ])
        if 'number' in response_data:
            log.warning('Erro durante a chamada do metodo get_entry_list do crm: %s' % response_data)
            raise self.CRMError('Erro durante a chamada do método get_entry_list do crm')
        return response_data

    def set_entry(self, tabela, campos):
        """
        Método genérico para inserir dados no CRM
        """
        response_data = self.call_crm('set_entry', [
            self.session_id,
            tabela,
            campos
        ])
        if 'id' not in response_data:
            log.warning('Erro durante a chamada do metodo set_entry do crm: %s' % response_data)
            raise self.CRMError('Erro durante a chamada do método set_entry do crm')
        return response_data

    def set_entry_account(self, cliente):
        """
        Cria uma account no CRM
        """
        response = self.set_entry('Accounts', {
            'corporate_tax_registry_c': cliente.cnpj,
            'name': cliente.razaosocial,
            'billing_address_street': cliente.logradouro,
            'billing_address_number_c': cliente.numero,
            'billing_address_complement_c': cliente.complemento,
            'billing_address_neighborhood_c': cliente.bairro,
            'billing_address_city': cliente.cidade,
            'billing_address_state': cliente.estado,
            'billing_address_country': cliente.pais,
            'billing_address_postalcode': cliente.cep,
            'sem_atividade_c': 1 if cliente.sem_atividade else 0,
        })

        return response['id']

    def set_entry_opportunities(self, oportunidade):
        """
        Cria uma opportunity no CRM
        """

        response = self.set_entry('Opportunities', {
            'account_id': oportunidade.account_id,
            'name': 'Oportunidade via e-commerce',
            #'ecommerce_id_c': oportunidade.numero_pedido, TODO: não existe ainda no CRM
            'date_closed': oportunidade.data_pedido,
            'amount': oportunidade.valor_total,

            # cartão de credito
            'titular_c': oportunidade.pag_credito_titular,
            'vencimento_c': oportunidade.pag_credito_vencimento,
            'bandeira_c': oportunidade.pag_credito_bandeira,
            'id_transacao_c': oportunidade.pag_credito_transacao_id,
            'ultimos_digitos_c': oportunidade.pag_credito_ultimos_digitos,

            #cartão de débito
            'titular_debito_c': oportunidade.pag_debito_titular,
            'vencimento_debito_c': oportunidade.pag_debito_vencimento,
            'bandeira_debito_c': oportunidade.pag_debito_bandeira,
            'transaction_id_debito_c': oportunidade.pag_debito_transacao_id,
            'ultimos_digitos_debito_c': oportunidade.pag_debito_ultimos_digitos,

            #boleto TODO: ainda requer ajustes no layout e campos por parte do CRM
        })

        return response['id']

    def set_entry_products(self, produto):
        """
        Cria um product no CRM
        """

        response = self.set_entry('Products', {
            'account_id': produto.account_id,
            'opportunities_id': produto.opportunity_id,
            'vendor_part_num': produto.codigo,
            'discount_price': produto.preco_venda,
            'quantity': produto.quantidade,
        })

        return response['id']

    def postar_compra(self, cliente, oportunidade, produtos):
        """
        Executa todo o processo de compra, criando account, opportunity e products quando necessário
        """
        self.login()
        try:
            account_id = self.get_account(cliente.cnpj)['entry_list']
            if account_id:
                account_id = account_id[0]['id']
            else:
                account_id = self.set_entry_account(cliente)

            oportunidade.account_id = account_id
            opportunity_id = self.set_entry_opportunities(oportunidade)

            for produto in produtos:
                produto.account_id = account_id
                produto.opportunity_id = opportunity_id
                self.set_entry_products(produto)
        except Exception as e:
            log.exception('Ocorreu um erro ao postar a compra')
        self.logout()

#print set_entry_account(
#    cnpj='88.888.888/0001-88',
#    razaosocial='Teste',
#    logradouro='rua teste',
#    numero='123',
#    complemento='complemento',
#    bairro='bairro teste',
#    cidade='cidade teste',
#    estado='SP',
#    pais='BR',
#    cep='04050-000',
#    sem_atividade=False
#)

#client = CRMClient()
#
#client.login()
#account = client.get_account('88.888.888/0001-88')['entry_list']
#client.logout()
#
#if account:
#    print account[0]['id']
#else:
#    print 'não encontrou'