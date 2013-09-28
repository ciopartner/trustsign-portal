# coding=utf-8
#from django.conf import settings
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


def get_entry_list(cnpj):
    session_id = login()
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
    logout(session_id)

    return response_data