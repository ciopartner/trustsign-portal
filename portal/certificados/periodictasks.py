# coding=utf-8
from __future__ import unicode_literals
import email
import imaplib
import os
from django.conf import settings
from periodically.decorators import every
from logging import getLogger

log = getLogger('portal.certificados.periodictasks')

@every(minutes=5)
def envia_comodo():
    from libs import comodo
    from portal.certificados.models import Emissao, Revogacao

    status_envio_pendente = (
        Emissao.STATUS_EMISSAO_ENVIO_COMODO_PENDENTE,
        Emissao.STATUS_REEMISSAO_ENVIO_COMODO_PENDENTE,
        Emissao.STATUS_REVOGACAO_ENVIO_COMODO_PENDENTE,
    )

    for emissao in Emissao.objects.select_related('voucher', 'revogacao').filter(emission_status=status_envio_pendente):
        try:
            if emissao.emission_status == Emissao.STATUS_EMISSAO_ENVIO_COMODO_PENDENTE:
                voucher = emissao.voucher
                # TODO: retirar if após implementar api comodo para os outros produtos
                if voucher.ssl_product not in (voucher.PRODUTO_SMIME, voucher.PRODUTO_CODE_SIGNING, voucher.PRODUTO_JRE):
                    resposta = comodo.emite_certificado(emissao)

                    emissao.comodo_order = resposta['orderNumber']
                    emissao.emission_cost = resposta['totalCost']
                    emissao.emission_status = Emissao.STATUS_EMISSAO_ENVIADO_COMODO

            elif emissao.emission_status == Emissao.STATUS_REEMISSAO_ENVIO_COMODO_PENDENTE:
                # Como o ambiente de testes não existe para reemissão...
                if not settings.COMODO_ENVIAR_COMO_TESTE:
                    comodo.reemite_certificado(emissao)
                    emissao.emission_status = emissao.STATUS_REEMISSAO_ENVIADO_COMODO
            else:
                try:
                    comodo.revoga_certificado(emissao.revogacao)
                    emissao.status = Emissao.STATUS_REVOGACAO_ENVIADO_COMODO

                except Revogacao.DoesNotExist:
                    log.error('Tentando revogar uma emissão sem criar a revogação no banco')

        except comodo.ComodoError as e:
            log.error('Ocorreu um erro(%s) na chamada da comodo da emissao: %s' % (e.code, emissao))

            emissao.emission_status = Emissao.OCORREU_ERRO_COMODO
            emissao.emission_error_message = '%s (%s)' % (e.comodo_message, e.code)

        emissao.save()


def check_email():
    m = imaplib.IMAP4_SSL("imap.gmail.com")
    m.login(settings.CERTIFICADOS_EMAIL_USERNAME, settings.CERTIFICADOS_EMAIL_PASSWORD)
    m.select("[Gmail]/Todos os e-mails")
    resp, items = m.search(None, '(FROM "noreply_support@comodo.com")')
    items = items[0].split()
    for emailid in items:
        resp, data = m.fetch(emailid, "(RFC822)")
        email_body = data[0][1]
        mail = email.message_from_string(email_body)

        if mail.get_content_maintype() != 'multipart':
            continue

        counter = 1

        for part in mail.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()

            if not filename:
                filename = 'part-%03d%s' % (counter, 'bin')
                counter += 1

            att_path = os.path.join(settings.CERTIFICADOS_EMAIL_PATH_ATTACHMENTS, filename)

            if not os.path.isfile(att_path):
                fp = open(att_path, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()