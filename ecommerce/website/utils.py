# coding=utf-8
from __future__ import unicode_literals
from collections import defaultdict
from xml.etree import cElementTree
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from libs import knu
import re

import logging

log = logging.getLogger('ecommerce.website.utils')


def remove_message(request, message_text):
    storage = messages.get_messages(request)
    for message in storage._queued_messages:
        if message.message == message_text:
            storage._queued_messages.remove(message)

def limpa_cpf(cpf):
    return re.sub('[.-]', '', cpf)

def limpa_cnpj(cnpj):
    return re.sub('[./-]', '', cnpj)


def limpa_telefone(telefone):
    return re.sub('[\(\) -]', '', telefone)


def formata_cnpj(cnpj):
    return '%s.%s.%s/%s-%s' % (cnpj[0:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:14])


def get_dados_empresa(cnpj):
    cnpj = limpa_cnpj(cnpj)
    data = cache.get('cnpj-%s' % cnpj)
    if data is None:
        if settings.USAR_KNU:
            r = knu.receitaCNPJ(cnpj)
            if r.cod_erro != 0:
                log.warning('Erro na requisição da knu: (%d) %s' % (r.cod_erro, r.desc_erro))
                return {'erro': 'Erro interno'}

            data = {
                'cnpj': cnpj,
                'razao_social': r.nome_empresarial,
                'logradouro': r.logradouro,
                'numero': r.numero,
                'complemento': r.complemento,
                'cep': r.cep,
                'bairro': r.bairro,
                'cidade': r.municipio,
                'uf': r.uf,
                'situacao_cadastral': r.situacao_cadastral,
                'knu_html': r.html
            }
        else:
            # somente para fins de testes:
            data = {
                'cnpj': cnpj,
                'razao_social': 'CIO Partner',
                'logradouro': 'Av. Dr. Candido Motta Filho',
                'numero': '856',
                'complemento': '1º andar',
                'cep': '05351010',
                'bairro': 'Vila São Francisco',
                'cidade': 'São Paulo',
                'uf': 'SP',
                'situacao_cadastral': 'ativa',
                'knu_html': '<html></html>'
            }
        cache.set('cnpj-%s' % cnpj, data, 2592000)  # cache de 30 dias
    return data


def xml_to_dict(xml):
    return etree_to_dict(cElementTree.XML(xml))


def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.iteritems():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.iteritems())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d