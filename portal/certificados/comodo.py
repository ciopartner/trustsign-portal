#coding=utf-8
from django.conf import settings
import requests
from portal.ferramentas.utils import url_parse


CODIGOS_PRODUTOS = {
    'ssl': 488,
    'ssl-wildcard': 489,
    'ssl-san': 492,
    'ssl-ev': 337,
    'ssl-ev-mdc': 410,
    'ssl-mdc': 335
}


def get_emails_validacao_padrao(dominio):
    emails_padroes = ('admin@%s', 'webmaster@%s', 'hostmaster@%s', 'postmaster@%s', 'administrator@%s')
    return [e % dominio for e in emails_padroes]


def emite_certificado(emissao):
    voucher = emissao.voucher

    if voucher.ssl_validade == voucher.VALIDADE_ANUAL:
        validade = 1
    elif voucher.ssl_validade == voucher.VALIDADE_BIANUAL:
        validade = 2
    elif voucher.ssl_validade == voucher.VALIDADE_TRIANUAL:
        validade = 3
    else:
        raise Exception('Validade inválida para emissão de certificados')

    params = {
        'loginName': settings.COMODO_LOGIN_NAME,
        'loginPassword': settings.COMODO_LOGIN_PASSWORD,
        'product': CODIGOS_PRODUTOS[voucher.ssl_produto],
        'years': validade,
        'serverSoftware': emissao.emissao_servidor_tipo,
        'csr': emissao.emissao_csr,
        'prioritiseCSRValues': 'N',
        'streetAddress1': voucher.cliente_logradouro,
        'localityName': voucher.cliente_cidade,
        'stateOrProvinceName': voucher.cliente_uf,
        'postalCode': voucher.cliente_cep,
        'countryName': 'BR',
        'emailAddress': 'none',
        'isCustomerValidated': 'Y',
        'foreignOrderNumber': emissao.crm_hash,
        #'checkFONIsUnique': 'Y', # comentei só pra ficar mais facil de testar, senao teria q criar um voucher toda hora
        'responseFormat': '1',
        'test': 'Y' if settings.COMODO_ENVIAR_COMO_TESTE else 'N',
        'isAppRepValidated': 'Y',
        'isCallbackCompleted': 'Y'
    }

    if voucher.ssl_produto in (voucher.PRODUTO_MDC, voucher.PRODUTO_SAN_UCC, voucher.PRODUTO_EV_MDC):
        params['domainNames'] = emissao.emissao_fqdns
        params['dcvEmailAddresses'] = emissao.emissao_validacao_email
    else:
        params['dcvEmailAddress'] = emissao.emissao_validacao_email

    if voucher.ssl_produto in (voucher.PRODUTO_EV, voucher.PRODUTO_EV_MDC):
        params['joiLocalityName'] = voucher.cliente_cidade
        params['joiStateOrProvinceName'] = voucher.cliente_uf
        params['joiCountryName'] = 'BR'

    response = requests.post(settings.COMODO_API_EMISSAO_URL, params)

    r = url_parse(response.text)
    if r['errorCode'] != '0':
        raise Exception('Ocorreu um erro na chamada da COMODO')
    return r