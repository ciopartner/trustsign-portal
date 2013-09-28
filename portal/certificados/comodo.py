#coding=utf-8
from __future__ import unicode_literals
from django.conf import settings
import requests
from portal.certificados.models import Voucher
from portal.ferramentas.utils import url_parse, get_emails_dominio

import logging

log = logging.getLogger('portal.certificados.comodo')

CODIGO_SSL = 488
CODIGO_SSL_WILDCARD = 489
CODIGO_SSL_SAN = 492
CODIGO_SSL_EV = 337
CODIGO_SSL_EV_MDC = 410
CODIGO_MDC = 335

CODIGOS_PRODUTOS = {
    Voucher.PRODUTO_SSL: CODIGO_SSL,
    Voucher.PRODUTO_SSL_WILDCARD: CODIGO_SSL_WILDCARD,
    Voucher.PRODUTO_SAN_UCC: CODIGO_SSL_SAN,
    Voucher.PRODUTO_EV: CODIGO_SSL_EV,
    Voucher.PRODUTO_EV_MDC: CODIGO_SSL_EV_MDC,
    Voucher.PRODUTO_MDC: CODIGO_MDC
}


class ComodoError(Exception):
    code = None

    def __init__(self, *args, **kwargs):
        self.code = kwargs.pop('code', -1)
        super(ComodoError, self).__init__(*args, **kwargs)


def get_emails_validacao_padrao(dominio):
    if dominio.startswith('*.'):
        dominio = dominio[2:]
    emails_padroes = ('admin@%s', 'administrator@%s', 'hostmaster@%s', 'postmaster@%s', 'webmaster@%s')
    return [e % dominio for e in emails_padroes]


def get_emails_validacao_whois(dominio):
    response = requests.post(settings.COMODO_API_GET_DCV_EMAILS_URL, data={
        'loginName': settings.COMODO_LOGIN_NAME,
        'loginPassword': settings.COMODO_LOGIN_PASSWORD,
        'domainName': dominio
    })
    return [r[12:] for r in response.text.splitlines()
            if r.startswith('whois email\t') and r[:12] not in ('cert@cert.br', 'mail-abuse@cert.br')]


def get_emails_validacao_whois(dominio):
    """
    Esse método esta aqui porque a API da comodo não está retornando os emails corretamente para dominios brasileiros
    então estamos fazendo direto no whois
    """
    return get_emails_dominio(dominio)


def get_emails_validacao(dominio):
    return get_emails_validacao_padrao(dominio) + get_emails_validacao_whois(dominio)


def emite_certificado(emissao):
    voucher = emissao.voucher

    if voucher.ssl_term == voucher.VALIDADE_ANUAL:
        validade = 1
    elif voucher.ssl_term == voucher.VALIDADE_BIANUAL:
        validade = 2
    elif voucher.ssl_term == voucher.VALIDADE_TRIANUAL:
        validade = 3
    else:
        raise Exception('Validade inválida para emissão de certificados', code=-1)

    params = {
        'loginName': settings.COMODO_LOGIN_NAME,
        'loginPassword': settings.COMODO_LOGIN_PASSWORD,
        'product': CODIGOS_PRODUTOS[voucher.ssl_product],
        'years': validade,
        'serverSoftware': emissao.emission_server_type,
        'csr': emissao.emission_csr,
        'prioritiseCSRValues': 'N',
        'streetAddress1': voucher.customer_address1,
        'localityName': voucher.customer_city,
        'stateOrProvinceName': voucher.customer_state,
        'postalCode': voucher.customer_zip,
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

    if voucher.ssl_product in (voucher.PRODUTO_MDC, voucher.PRODUTO_SAN_UCC, voucher.PRODUTO_EV_MDC):
        params['domainNames'] = emissao.emission_fqdns
        params['dcvEmailAddresses'] = emissao.emission_dcv_emails
    else:
        params['dcvEmailAddress'] = emissao.emission_dcv_emails

    if voucher.ssl_product in (voucher.PRODUTO_EV, voucher.PRODUTO_EV_MDC):
        params['joiLocalityName'] = voucher.customer_city
        params['joiStateOrProvinceName'] = voucher.customer_state
        params['joiCountryName'] = 'BR'

    response = requests.post(settings.COMODO_API_EMISSAO_URL, params)

    r = url_parse(response.text)
    if r['errorCode'] != '0':
        log.error(r)
        log.error('Ocorreu um erro na chamada da COMODO, parametros: %s' % params)
        raise ComodoError('Ocorreu um erro na chamada da COMODO', code=r['errorCode'])
    return r


def revoga_certificado(revogacao):

    params = {
        'loginName': settings.COMODO_LOGIN_NAME,
        'loginPassword': settings.COMODO_LOGIN_PASSWORD,
        'orderNumber': revogacao.emissao.comodo_order,
        'revocationReason': revogacao.revogacao_motivo,
        'test': 'Y' if settings.COMODO_ENVIAR_COMO_TESTE else 'N',
        'responseFormat': '1',
    }

    response = requests.post(settings.COMODO_API_REVOGACAO_URL, params)

    r = url_parse(response.text)
    if r['errorCode'] != '0':
        log.error(r)
        log.error('Ocorreu um erro na chamada da COMODO, parametros: %s' % params)
        raise ComodoError('Ocorreu um erro na chamada da COMODO', code=r['errorCode'])
    return r


def reemite_certificado(emissao):

    params = {
        'loginName': settings.COMODO_LOGIN_NAME,
        'loginPassword': settings.COMODO_LOGIN_PASSWORD,
        'orderNumber': emissao.comodo_order,
        'csr': emissao.emission_csr,
        'isCustomerValidated': 'Y',
        'foreignOrderNumber': emissao.crm_hash,
        'responseFormat': '1',
        'isAppRepValidated': 'Y',
        'isCallbackCompleted': 'Y'
    }

    response = requests.post(settings.COMODO_API_REEMISSAO_URL, params)

    r = url_parse(response.text)
    if r['errorCode'] != '0':
        log.error(r)
        log.error('Ocorreu um erro na chamada da COMODO, parametros: %s' % params)
        raise ComodoError('Ocorreu um erro na chamada da COMODO', code=r['errorCode'])
    return r