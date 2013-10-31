# coding=utf-8
from __future__ import unicode_literals
from datetime import date
from time import time
import email
import imaplib
import os
import re
from django.conf import settings
from logging import getLogger
from django_cron import CronJobBase, Schedule

log = getLogger('portal.certificados.crons')


class EnviaComodoJob(CronJobBase):
    """
    Envia para a comodo as emissões com status aguardando envio comodo.
    """
    RUN_EVERY_MINS = 10

    code = 'certificados.envia_comodo'
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)

    def do(self):
        from libs import comodo
        from ecommerce.certificados.models import Emissao, Revogacao

        status_envio_pendente = (
            Emissao.STATUS_EMISSAO_ENVIO_COMODO_PENDENTE,
            Emissao.STATUS_REEMISSAO_ENVIO_COMODO_PENDENTE,
            Emissao.STATUS_REVOGACAO_ENVIO_COMODO_PENDENTE,
        )

        for emissao in Emissao.objects.select_related('voucher', 'revogacao').filter(
                emission_status__in=status_envio_pendente):
            try:
                if emissao.emission_status == Emissao.STATUS_EMISSAO_ENVIO_COMODO_PENDENTE:
                    voucher = emissao.voucher
                    # TODO: retirar if após implementar api comodo para os outros produtos
                    if voucher.ssl_product not in (voucher.PRODUTO_SMIME,
                                                   voucher.PRODUTO_CODE_SIGNING,
                                                   voucher.PRODUTO_JRE):
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


class CheckEmailJob(CronJobBase):
    """
    Verifica se existem novos certificados no email configurado na comodo.
    """
    RUN_EVERY_MINS = 60

    code = 'certificados.check_email'
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)

    def do(self):
        from ecommerce.certificados.models import Emissao

        #  http://stackoverflow.com/questions/348630/how-can-i-download-all-emails-with-attachments-from-gmail
        m = imaplib.IMAP4_SSL(settings.CERTIFICADOS_IMAP_SERVER)
        m.login(settings.CERTIFICADOS_EMAIL_USERNAME, settings.CERTIFICADOS_EMAIL_PASSWORD)
        m.select("INBOX")
        resp, items = m.search(None, '(FROM "noreply_support@comodo.com") (UNSEEN)')
        items = items[0].split()

        for emailid in items:
            resp, data = m.fetch(emailid, "(RFC822)")
            email_body = data[0][1]
            mail = email.message_from_string(email_body)

            if mail.get_content_maintype() != 'multipart':
                continue

            subject = mail.get('subject')

            try:
                comodo_order = re.match('.*ORDER #([0-9]+).*', subject).groups(0)[0]
                emissao = Emissao.objects.select_related('voucher').get(comodo_order=comodo_order)

                text_content = str(list(mail.get_payload()[0].walk())[1])
                certificado = re.match('.*(-----BEGIN CERTIFICATE-----.*-----END CERTIFICATE-----).*',
                                       text_content, re.S).groups(0)[0]

                emissao.emission_certificate = certificado

                counter = 1

                for part in mail.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue

                    filename = part.get_filename()

                    if not filename:
                        filename = 'part-%03d%s' % (counter, '.bin')
                        counter += 1
                    ano = str(date.today().year)
                    mes = str(date.today().month)
                    directory = os.path.join(settings.CERTIFICADOS_EMAIL_PATH_ATTACHMENTS, ano, mes)

                    if not os.path.exists(directory):
                        os.makedirs(directory)

                    timestamp = str(time()).replace('.', '')
                    s = filename.split('.')
                    filename = s[:-1]
                    ext = s[-1]

                    att_path = os.path.join(directory, '%s-%s.%s' % (filename, timestamp, ext))

                    if not os.path.isfile(att_path):
                        fp = open(att_path, 'wb')
                        fp.write(part.get_payload(decode=True))
                        fp.close()
                    emissao.emission_mail_attachment_path = att_path

                emissao.save()

            except (IndexError, AttributeError):
                log.error('Recebeu e-mail fora do padrão')
            except Emissao.DoesNotExist:
                log.error('Recebeu e-mail com comodo order inexistente no banco')