# coding=utf-8
#from django.conf import settings
import requests
import json
from logging import getLogger

log = getLogger('libs.crm')


class CRMError(Exception):
    pass


def login(canal="Portal"):
    response = requests.post('http://dev2.lampadaglobal.com/projects/trustsign/service/v4_1/rest.php', {
        'method': 'login',
        'input_type': 'json',
        'response_type': 'json',
        'rest_data': json.dumps([
            {
                'user_name': 'ceo',  # settings.CRM_USERNAME,
                'password': '26442effb42e24d42f179f343c89e419',  # settings.CRM_PASSWORD_HASH,
            },
            canal
        ])
    })
    response_data = response.json()
    if 'id' not in response_data:
        log.warning('Erro durante a chamada do metodo login do crm: %s' % response_data)
        raise CRMError('Erro durante a chamada do método login do crm')
    return response_data['id']