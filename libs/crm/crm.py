# coding=utf-8
from __future__ import unicode_literals
from django.conf import settings
import requests
import json
from logging import getLogger
import re

log = getLogger('libs.crm')


def escape(valor):
    return re.sub(r'([\'\"\\])', r'\\\1', valor)


class ClienteCRM(object):

    TIPOS_NEGOCIO = (
        ('Alimentos', 'Alimentos'),
        ('Environmental', 'Ambiental'),
        ('Banking', 'Banco'),
        ('Biotechnology', 'Biotecnologia'),
        ('Communications', 'Comunicações'),
        ('Construction', 'Construção'),
        ('Consulting', 'Consultoria'),
        ('ECommerce', 'E-Commerce'),
        ('Electronics', 'Electrônicos'),
        ('Energy', 'Energia'),
        ('Engineering', 'Engenharia'),
        ('Education', 'Ensino'),
        ('Entertainment', 'Entretenimento'),
        ('Finance', 'Financeira'),
        ('Government', 'Governo'),
        ('Hospitality', 'Hotelaria'),
        ('Internet', 'Internet'),
        ('Manufacturing', 'Manufatura'),
        ('Machinery', 'Maquinaria'),
        ('Media', 'Meios de Comunicação'),
        ('Shipping', 'Navegação'),
        ('Other', 'Outros'),
        ('Chemicals', 'Química'),
        ('Recreation', 'Recreação'),
        ('Healthcare', 'Saúde'),
        ('Insurance', 'Seguros'),
        ('Not For Profit', 'Sem Fins Lucrativos'),
        ('Servicos', 'Serviços'),
        ('Utilities', 'Serviços Públicos'),
        ('Technology', 'Tecnologia'),
        ('Telecommunications', 'Telecomunicações'),
        ('Apparel', 'Têxtil'),
        ('Transportation', 'Transportes'),
        ('Turismo', 'Turismo'),
        ('Retail', 'Varejo'),
    )

    FONTES_DO_POTENCIAL = (
        ('Abraweb', 'Abraweb'),
        ('Acoes de Marketing', 'Ações de Marketing'),
        ('Buscadores', 'Buscadores'),
        ('Canal', 'Canal'),
        ('Chat', 'Chat'),
        ('ECommerce Brasil', 'E-Commerce Brasil'),
        ('Eventos', 'Eventos'),
        ('Inside Sales', 'Inside Sales'),
        ('Parceiro', 'Parceiro'),
        ('Site de Clientes', 'Site de Clientes'),
        ('Website', 'Website'),
    )

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
        self.tipo_negocio = None
        self.is_ecommerce = None
        self.fonte_do_potencial = None


class OportunidadeCRM(object):
    TIPO_CARTAO_CREDITO = 'cartao_credito'
    TIPO_CARTAO_DEBITO = 'cartao_debito'
    TIPO_BOLETO = 'boleto_bancario'

    def __init__(self):
        self.account_id = None
        self.contact_id = None
        self.numero_pedido = None
        self.data_pedido = None
        self.valor_total = None
        self.tipo_pagamento = None

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
        self.nosso_numero = None
        self.data_pagamento_boleto = None

    @property
    def name(self):
        return 'Oportunidade via e-commerce ({})'.format(self.numero_pedido)

    def is_credito(self):
        return self.tipo_pagamento == self.TIPO_CARTAO_CREDITO

    def is_debito(self):
        return self.tipo_pagamento == self.TIPO_CARTAO_DEBITO

    def is_boleto(self):
        return self.tipo_pagamento == self.TIPO_BOLETO


class ProdutoCRM(object):

    def __init__(self):
        self.account_id = None
        self.opportunity_id = None
        self.codigo = None
        self.preco_unitario = None
        self.preco_total = None
        self.quantidade = None


class ContatoCRM(object):

    def __init__(self):
        self.account_id = None
        self.nome = None
        self.sobrenome = None
        self.telefone = None
        self.email = None


class CRMClient(object):

    def __init__(self):
        self.session_id = None

    class CRMError(Exception):
        """
        Ocorreu um erro na integração com o CRM
        """
        pass

    def call_crm(self, method, rest_data, input_type='json', response_type='json'):
        """
        Todos os métodos usam este para executar a chamada ao CRM
        """
        response = None

        if settings.DEBUG:
            log.info('\n\nMetodo: {}'.format(method))
            log.info('Request ao Sugar: {}'.format(rest_data))

        if not self.session_id and method != 'login':
            raise self.CRMError('Desconectado')

        try:
            response = requests.post(settings.CRM_URL, {
                'method': method,
                'input_type': input_type,
                'response_type': response_type,
                'rest_data': json.dumps(rest_data)
            })

            resposta = response.json()

        except Exception as e:
            log.exception('Ocorreu um erro na chamada do crm: %s' % response.text if response is not None else '')
            raise self.CRMError('Ocorreu um erro na chamada do metodo %s na CRM, verifique o log' % method)

        if settings.DEBUG:
            log.info('Response: {}'.format(resposta))

        return resposta

    def login(self, canal="Portal"):
        """
        Inicia a sessão
        """
        response_data = self.call_crm('login', [
            {
                'user_name': settings.CRM_USERNAME,
                'password': settings.CRM_PASSWORD_HASH,
            },
            canal
        ])

        if 'id' not in response_data:
            log.warning('User: {}, Password: ***'.format(settings.CRM_USERNAME))
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

    def get_entry_list(self, modulo, where, order_by='', offset=0, select_fields=None, link_name_to_fields_array=None,
                       max_results=0, deleted=0, favorites=False):

        if select_fields is None:
            select_fields = []

        if link_name_to_fields_array is None:
            link_name_to_fields_array = []

        response_data = self.call_crm('get_entry_list', [
            self.session_id,
            modulo,
            where,
            order_by,
            offset,
            select_fields,
            link_name_to_fields_array,
            max_results,
            deleted,
            favorites
        ])

        if 'number' in response_data:
            log.warning('Erro durante a chamada do metodo get_entry_list do crm: %s' % response_data)
            raise self.CRMError('Erro durante a chamada do método get_entry_list do crm')

        return response_data

    def get_account(self, cnpj):
        """
        Retorna dados de uma Account
        """
        return self.get_entry_list(modulo='Accounts',
                                   where='accounts_cstm.corporate_tax_registry_c = \'%s\'' % escape(cnpj),
                                   select_fields=['id', 'name'],
                                   max_results=1)

    def get_contact(self, account_id, nome, sobrenome):
        """
        Retorna dados de uma Contact
        """
        return self.get_entry_list(modulo='Contacts',
                                   where='contacts.first_name = \'%s\' AND contacts.last_name = \'%s\'' % (escape(nome), escape(sobrenome)),
                                   select_fields=['id'],
                                   max_results=1)

    def get_contract(self, crm_hash):
        """
        Retorna dados de um Contract
        """
        return self.get_entry_list(modulo='Contracts',
                                   where='contracts.id = %s' % crm_hash,
                                   select_fields=['id'],
                                   max_results=1)

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
            'account_type': 'Cliente',
            'industry': cliente.tipo_negocio,
            'e_commerce_c': cliente.is_ecommerce,
            'lead_source': cliente.fonte_do_potencial,
        })

        return response['id']

    def set_entry_opportunities(self, oportunidade):
        """
        Cria uma opportunity no CRM
        """

        data = {
            'account_id': oportunidade.account_id,
            'assigned_user_id': settings.CRM_OPORTUNITY_ASSIGNED_USER_ID,
            'manufacturers_id': settings.CRM_OPORTUNITY_MANUFACTURERS_ID,
            'name': 'Oportunidade via e-commerce',
            'ecommerce_id_c': oportunidade.numero_pedido,  # TODO: não existe ainda no CRM
            'date_closed': oportunidade.data_pedido,
            'amount': oportunidade.valor_total,
            'tipo_pagamento_c': oportunidade.tipo_pagamento,
            'sales_stage': 'Closed Won',
            'opportunity_type': 'New Business',
        }

        response = self.set_entry('Opportunities', data)

        if oportunidade.is_credito():
            data.update({
                'titular_c': oportunidade.pag_credito_titular,
                'vencimento_c': oportunidade.pag_credito_vencimento,
                'bandeira_c': oportunidade.pag_credito_bandeira,
                'id_transacao_c': oportunidade.pag_credito_transacao_id,
                'ultimos_digitos_c': oportunidade.pag_credito_ultimos_digitos,
            })
        elif oportunidade.is_debito():
            data.update({
                'titular_debito_c': oportunidade.pag_debito_titular,
                'vencimento_debito_c': oportunidade.pag_debito_vencimento,
                'bandeira_debito_c': oportunidade.pag_debito_bandeira,
                'transaction_id_debito_c': oportunidade.pag_debito_transacao_id,
                'ultimos_digitos_debito_c': oportunidade.pag_debito_ultimos_digitos,
            })
        elif oportunidade.is_boleto():
            data.update({
                'nosso_numero_c': oportunidade.nosso_numero,
                'data_pgto_c': oportunidade.data_pagamento_boleto
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
            'discount_price': produto.preco_unitario,
            'discount_amount': produto.preco_total,
            'quantity': produto.quantidade,
        })

        return response['id']

    def set_entry_contact(self, contato):
        """
        Cria um contact no CRM
        """
        response = self.set_entry('Contacts', {
            'account_id': contato.account_id,
            'first_name': contato.nome,
            'last_name': contato.sobrenome,
            'phone_work': contato.telefone,
            'email1': contato.email
            #'phone_mobile': contato.celular,
            #'title': contato.cargo,
            #'department': contato.departamento
        })

        return response['id']

    def update_contract(self, crm_hash, status, seal_html=None, certificate_file=None):
        data = {
            'id': crm_hash,
            'status': status
        }

        if seal_html is not None:
            data['seal_html_c'] = seal_html

        self.set_entry('Contracts', data)

    def get_or_create_account(self, cliente):
        account_id = self.get_account(cliente.cnpj)['entry_list']

        return account_id[0]['id'] if account_id else self.set_entry_account(cliente)

    def get_or_create_contact(self, contato):

        contact_id = self.get_contact(contato.account_id, contato.nome, contato.sobrenome)['entry_list']

        return contact_id[0]['id'] if contact_id else self.set_entry_contact(contato)

    def postar_compra(self, cliente, contato, oportunidade, produtos):
        """
        Executa todo o processo de compra, criando account, opportunity e products quando necessário
        """
        log.info('Iniciando a postagem do pedido #%s' % oportunidade.numero_pedido)

        try:
            self.login()

            account_id = self.get_or_create_account(cliente)

            contato.account_id = account_id
            contact_id = self.get_or_create_contact(contato)

            oportunidade.account_id = account_id
            oportunidade.countact_id = contact_id
            opportunity_id = self.set_entry_opportunities(oportunidade)

            for produto in produtos:
                produto.account_id = account_id
                produto.opportunity_id = opportunity_id
                self.set_entry_products(produto)

            self.logout()

        except Exception as e:
            log.exception('Ocorreu um erro ao postar a compra')
            raise self.CRMError('Ocorreu um erro ao postar a compra, verifique o log')

        log.info('Finalizando a postagem do pedido #%s' % oportunidade.numero_pedido)

    def atualizar_contrato(self, crm_hash, status, seal_html=None, certificate_file=None):
        log.info('Atualizando o contrato #%s' % crm_hash)

        try:
            self.login()

            self.update_contract(crm_hash, status, seal_html, certificate_file)

            self.logout()

        except Exception as e:
            log.exception('Ocorreu um erro ao atualizar o contrato')
            raise self.CRMError('Ocorreu um erro ao atualizar o contrato, verifique o log')

        log.info('Atualização do contrato #%s concluída' % crm_hash)