# coding=utf-8
#from django.conf import settings
from __future__ import unicode_literals
import requests
import json
from logging import getLogger

log = getLogger('libs.crm')


class CRMError(Exception):
    pass


def call_crm(method, rest_data, url='http://dev2.lampadaglobal.com/projects/trustsign/service/v4_1/rest.php',
             input_type='json', response_type='json'):

    response = requests.post(url, {
        'method': method,
        'input_type': input_type,
        'response_type': response_type,
        'rest_data': json.dumps(rest_data)
    })

    return response.json()


def login(canal="Portal"):
    response_data = call_crm('login', [
        {
            'user_name': 'ceo',  # settings.CRM_USERNAME,
            'password': '26442effb42e24d42f179f343c89e419',  # settings.CRM_PASSWORD_HASH,
        },
        canal
    ])
    if 'id' not in response_data:
        log.warning('Erro durante a chamada do metodo login do crm: %s' % response_data)
        raise CRMError('Erro durante a chamada do método login do crm')
    return response_data['id']


def logout(session_id):
    call_crm('logout', [session_id])


def get_entry_list(session_id, cnpj):
    response_data = call_crm('get_entry_list', [
        session_id,
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
        raise CRMError('Erro durante a chamada do método get_entry_list do crm')
    return response_data


def set_entry(session_id, tabela, campos):
    response_data = call_crm('set_entry', [
        session_id,
        tabela,
        campos
    ])
    if 'id' not in response_data:
        log.warning('Erro durante a chamada do metodo set_entry do crm: %s' % response_data)
        raise CRMError('Erro durante a chamada do método set_entry do crm')
    return response_data


def set_entry_account(session_id, cliente):
    response = set_entry(session_id, 'Accounts', {
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


def set_entry_opportunities(session_id, oportunidade):

    return {}


def set_entry_products(session_id, produto):

    return {}

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
session_id = login()
cliente = get_entry_list(session_id, '88.888.888/0001-88')['entry_list']
logout(session_id)
if cliente:
    print cliente[0]['id']
else:
    print 'não encontrou'


def postar_compra(cliente, oportunidade, produtos):
    session_id = login()
    account_id = get_entry_list(session_id, cliente.cnpj)['entry_list']
    if account_id:
        account_id = account_id[0]['id']
    else:
        account_id = set_entry_account(session_id, cliente)
    oportunidade.account_id = account_id
    opportunitie_id = set_entry_opportunities(session_id, oportunidade)
    for produto in produtos:
        produto.account_id = account_id
        produto.opportunitie_id = opportunitie_id
        set_entry_products(session_id, produto)

    logout(session_id)