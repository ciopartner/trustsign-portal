# coding=utf-8
from __future__ import unicode_literals
from time import time
import email
import imaplib
import os
import re
from django.conf import settings
from logging import getLogger
from django.contrib.auth import get_user_model
from django.contrib.sites.models import get_current_site
from django.core.mail import send_mail, EmailMessage
from django.template.context import Context
from django.template.loader import get_template
from django_cron import CronJobBase, Schedule
import requests
from django.utils.timezone import now
from ecommerce.website.utils import send_template_email, get_template_email
from libs.crm.crm import CRMClient

log = getLogger('portal.certificados.crons')


class EnviaComodoJob(CronJobBase):
    """
    Envia para a comodo as emissões com status aguardando envio comodo.
    """
    RUN_EVERY_MINS = 1

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

                emissao.emission_status = Emissao.STATUS_OCORREU_ERRO_COMODO
                emissao.emission_error_message = '%s (%s)' % (e.comodo_message, e.code)

            emissao.save()


class CheckEmailJob(CronJobBase):
    """
    Verifica se existem novos certificados no email configurado na comodo.
    """
    RUN_EVERY_MINS = 1

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
                    if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                        continue

                    emissao.emission_mail_attachment_path = self.extract_attachment(part, counter)

                emissao.emission_status = Emissao.STATUS_EMITIDO_SELO_PENDENTE

                emissao.save()
                self.envia_email_usuario(emissao)

            except (IndexError, AttributeError):
                log.error('Recebeu e-mail fora do padrão (#{})'.format(subject))
            except Emissao.DoesNotExist:
                log.error('Recebeu e-mail com comodo order inexistente no banco (#{}) '.format(subject))

    def extract_attachment(self, part, counter):
        filename = part.get_filename()

        if not filename:
            filename = 'part-%03d%s' % (counter, '.bin')
            counter += 1

        n = now()
        ano = str(n.year)
        mes = str(n.month)
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

        return att_path

    def envia_email_usuario(self, emissao):
        User = get_user_model()
        voucher = emissao.voucher
        try:
            user = User.objects.get(username=voucher.customer_cnpj)
            subject = 'Emissão Concluída'
            template = 'emails/emissao_solicitada_sucesso.html'
            context = {
                'voucher': voucher,
                'site': get_current_site(None),
            }
            msg = get_template_email([user.email], subject, template, context)
            msg.attach_file(emissao.emission_mail_attachment_path)
            msg.send()
        except User.DoesNotExist:
            log.warning('Emissão concluída de um CNPJ sem usuário cadastrado: {}'.format(voucher.customer_cnpj))


def chunks(l, n):
    """
    Generator that yields successive n-sized chunks from l.
    list(chunks(range(5), 2)) == [[0,1], [2,3] [4]]
    """
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


class AtivaSelosJob(CronJobBase):
    """
    Ativa os selos dos vouchers pendentes no servidor de selos.
    """
    RUN_EVERY_MINS = 1

    code = 'certificados.ativa_selo'
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)

    error_message = 'Ocorreu um exceção ao executar o cronjob AtivaSelos'

    def do(self):
        try:
            websites = self.extrai_websites()

            for line in ('basic', 'pro', 'prime'):
                lista = list(websites[line])
                if lista:
                    for chunk in chunks(lista, settings.SEALS_MAX_WEBSITES_PER_REQUEST):
                        self.processa(line, chunk)
            self.post_do()
        except Exception as e:
            log.exception(self.error_message)
            raise e  # joga a exceção novamente para o django-cron tentar executar o job
                     # novamente depois de alguns minutos e enviar o email de aviso

    def post_do(self):
        from ecommerce.certificados.models import Emissao

        for voucher in self._vouchers:
            voucher.emissao.emission_status = Emissao.STATUS_EMITIDO
            voucher.emissao.save()
            self.processa_ativado(voucher)

    def get_queryset(self):
        from ecommerce.certificados.models import Voucher, Emissao

        self._vouchers = Voucher.objects.select_related('emissao').filter(emissao__emission_status=Emissao.STATUS_EMITIDO_SELO_PENDENTE)
        return self._vouchers

    def extrai_websites(self):
        """
        Retorna um dict separando as urls pela linha, para envio ao servidor de selos
        """
        from ecommerce.certificados.models import Voucher

        websites = {
            'basic': set(),
            'pro': set(),
            'prime': set(),
        }

        for voucher in self.get_queryset():
            if voucher.ssl_product in (Voucher.PRODUTO_MDC, Voucher.PRODUTO_EV_MDC, Voucher.PRODUTO_SAN_UCC):
                if voucher.emissao.emission_urls:
                    websites[voucher.ssl_line].update(voucher.emissao.get_lista_dominios())
                else:
                    log.warning('voucher multi-dominio sem urls #%s' % voucher.pk)

            if voucher.ssl_product != Voucher.PRODUTO_SAN_UCC:
                websites[voucher.ssl_line].add(voucher.emissao.emission_url)

        return websites

    def processa(self, line, chunk):
        requests.post('%s/api/v1/ativar/%s/' % (settings.SEALS_SERVER_URL, line), {
            'username': settings.SEALS_USERNAME,
            'password': settings.SEALS_PASSWORD,
            'websites': ','.join(chunk)
        })

    def processa_ativado(self, voucher):
        # TODO: decidir onde atualizar o contrato da reemissão, e como enviar o arquivo para o CRM
        self.atualiza_contrato(voucher, 'valido', seal_html=voucher.get_seal_html)
        self.envia_email_cliente(voucher)

    def atualiza_contrato(self, voucher, status, seal_html=None, certificate_file=None):
        try:
            client = CRMClient()
            client.atualizar_contrato(voucher.crm_hash, status, seal_html, certificate_file)
        except Exception as e:
            log.exception('Ocorreu um erro ao atualizar o contrato do voucher #%s para o status <%s>' % (voucher.crm_hash, status))
            self.envia_email_suporte(voucher, status)

    def envia_email_cliente(self, voucher):
        html_content = get_template('emails/envio_certificado_e_selo.html')
        email_cliente = voucher.emissao.emission_publickey_sendto
        context = Context({
            'voucher': voucher,  # TODO: ver com o Carlos o que vai ser necessário passar pro template
        })
        msg = EmailMessage('Certificado Digital e Selo TrustSign', html_content.render(context), to=[email_cliente])
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

    def envia_email_suporte(self, voucher, status):
        message = 'Ocorreu um erro ao atualizar o contrato no CRM do voucher #%s para o status <%s>\ncliente: %s' % (voucher.crm_hash,
                                                                                                                     status,
                                                                                                                     voucher.customer_companyname)
        send_mail('[Alerta-CRM] #%s' % voucher.crm_hash, message, settings.DEFAULT_FROM_EMAIL, [settings.TRUSTSIGN_SUPORTE_EMAIL])


class DesativaSelosRevogadosJob(AtivaSelosJob):
    RUN_EVERY_MINS = 1

    code = 'certificados.desativa_selo'
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)

    error_message = 'Ocorreu um exceção ao executar o cronjob DesativaSelosRevogados'

    def get_queryset(self):
        from ecommerce.certificados.models import Voucher, Emissao

        self._vouchers = Voucher.objects.select_related('emissao').filter(emissao__emission_status=Emissao.STATUS_REVOGADO_SELO_PENDENTE)
        return self._vouchers

    def processa(self, line, websites):
        requests.post('%s/api/v1/desativar/%s/' % (settings.SEALS_SERVER_URL, line), {
            'username': settings.SEALS_USERNAME,
            'password': settings.SEALS_PASSWORD,
            'websites': ','.join(websites)
        })

    def post_do(self):
        from ecommerce.certificados.models import Emissao

        for voucher in self._vouchers:
            voucher.emissao.emission_status = Emissao.STATUS_REVOGADO
            voucher.emissao.save()
            self.processa_revogado(voucher)

    def processa_revogado(self, voucher):
        self.atualiza_contrato(voucher, 'revogado')


class DesativaSelosExpiradosJob(DesativaSelosRevogadosJob):

    code = 'certificados.desativa_selo_expirado'
    schedule = Schedule(run_at_times=['0:00'])

    error_message = 'Ocorreu um exceção ao executar o cronjob DesativaSelosExpirados'

    def get_queryset(self):
        from ecommerce.certificados.models import Voucher, Emissao

        self._vouchers = Voucher.objects.select_related('emissao').filter(
            emissao__emission_status=Emissao.STATUS_EMITIDO,
            ssl_valid_to__lt=now()
        )
        return self._vouchers

    def post_do(self):
        from ecommerce.certificados.models import Emissao

        for voucher in self._vouchers:
            voucher.emissao.emission_status = Emissao.STATUS_EXPIRADO
            voucher.emissao.save()
            self.processa_expirado(voucher)

    def processa_expirado(self, voucher):
        self.atualiza_contrato(voucher, 'expirado')