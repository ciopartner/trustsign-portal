# coding=utf-8
from __future__ import unicode_literals
from collections import defaultdict
from xml.etree import cElementTree
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import get_template
from libs import knu
import re

import logging
from libs.crm import crm

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


def limpa_cep(cep):
    return re.sub('[.-]', '', cep)


def limpa_telefone(telefone):
    return re.sub('[\(\) -]', '', telefone)


def formata_cnpj(cnpj):
    if len(cnpj) == 14:
        return '{}.{}.{}/{}-{}'.format(cnpj[:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:14])
    return cnpj


def formata_cep(cep):
    if len(cep) == 8:
        return '{}-{}'.format(cep[:5], cep[5:])
    return cep


def get_dados_empresa(cnpj):
    # Se não colocar o str() dá pau em produção
    cnpj = str(limpa_cnpj(cnpj))
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
                'nome_fantasia': r.titulo_estabelecimento,
                'logradouro': r.logradouro,
                'numero': r.numero,
                'complemento': r.complemento,
                'cep': limpa_cep(r.cep),
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
                'nome_fantasia': 'CIO Partner',
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
        cache.set('cnpj-%s' % cnpj, data, 604800)  # cache de 7 dias
    return data


def atualiza_dados_cliente(user):
    profile = user.get_profile()
    d = get_dados_empresa(profile.cliente_cnpj)
    mudou = False

    if profile.cliente_razaosocial != d['razao_social']:
        profile.cliente_razaosocial = d['razao_social']
        mudou = True

    if profile.cliente_nomefantasia != d['nome_fantasia']:
        profile.cliente_nomefantasia = d['nome_fantasia']
        mudou = True

    if profile.cliente_logradouro != d['logradouro']:
        profile.cliente_logradouro = d['logradouro']
        mudou = True

    if profile.cliente_numero != d['numero']:
        profile.cliente_numero = d['numero']
        mudou = True

    if profile.cliente_complemento != d['complemento']:
        profile.cliente_complemento = d['complemento']
        mudou = True

    if profile.cliente_cep != d['cliente_cep']:
        profile.cliente_cep = d['cliente_cep']
        mudou = True

    if profile.cliente_bairro != d['bairro']:
        profile.cliente_bairro = d['bairro']
        mudou = True

    if profile.cliente_cidade != d['cidade']:
        profile.cliente_cidade = d['cidade']
        mudou = True

    if profile.cliente_uf != d['uf']:
        profile.cliente_uf = d['uf']
        mudou = True

    if profile.cliente_situacao_cadastral != d['situacao_cadastral']:
        profile.cliente_situacao_cadastral = d['situacao_cadastral']
        mudou = True

    if mudou:
        c = crm.ClienteCRM()
        c.cnpj = formata_cnpj(profile.cliente_cnpj) if len(profile.cliente_cnpj) < 18 else profile.cliente_cnpj
        c.razaosocial = profile.cliente_razaosocial
        c.nomefantasia = profile.cliente_nomefantasia
        c.logradouro = profile.cliente_logradouro
        c.numero = profile.cliente_numero
        c.complemento = profile.cliente_complemento
        c.bairro = profile.cliente_bairro
        c.cidade = profile.cliente_cidade
        c.estado = profile.cliente_uf
        c.pais = 'BR'
        c.cep = profile.cliente_cep
        c.sem_atividade = profile.cliente_situacao_cadastral.strip().lower() == 'ativa'

        c.tipo_negocio = profile.cliente_tipo_negocio
        c.is_ecommerce = profile.cliente_ecommerce
        c.fonte_do_potencial = profile.cliente_fonte_potencial

        client = crm.CRMClient()
        client.login()
        account_id = client.get_account(c.cnpj)['entry_list']
        client.set_entry_account(c, update_id=account_id)
        client.logout()


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


def get_template_email(to, subject, template, context, from_email=None, bcc=None,
                       connection=None, attachments=None, headers=None, cc=None):
    html_content = get_template(template)
    context = Context(context)
    msg = EmailMessage(subject, html_content.render(context), from_email=from_email,
                       to=to, bcc=bcc, connection=connection, attachments=attachments, headers=headers, cc=cc)
    msg.content_subtype = 'html'
    return msg


def send_template_email(to, subject, template, context, from_email=None, bcc=None,
                        connection=None, attachments=None, headers=None, cc=None):
    msg = get_template_email(to, subject, template, context, from_email, bcc, connection, attachments, headers, cc)
    msg.send()