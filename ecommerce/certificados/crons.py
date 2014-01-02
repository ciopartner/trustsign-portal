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
from django.core.mail import send_mail
from django.utils import translation
from django_cron import CronJobBase, Schedule
import requests
from django.utils.timezone import now
from ecommerce.website.utils import get_template_email
from libs.crm.crm import CRMClient
from libs.ssl_utils import certificate_decode

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

        cur_language = translation.get_language()
        try:
            translation.activate('pt_BR')

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

                    emissao.set_erro_comodo('%s (%s)' % (e.comodo_message, e.code))

                emissao.save()
        finally:
            translation.activate(cur_language)


class CheckEmailJob(CronJobBase):
    """
    Verifica se existem novos certificados no email configurado na comodo.
    """
    RUN_EVERY_MINS = 1

    code = 'certificados.check_email'
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)

    def do(self):
        #  http://stackoverflow.com/questions/348630/how-can-i-download-all-emails-with-attachments-from-gmail

        from ecommerce.certificados.models import Emissao

        cur_language = translation.get_language()
        try:
            translation.activate('pt_BR')

            m = imaplib.IMAP4_SSL(settings.CERTIFICADOS_IMAP_SERVER)
            m.login(settings.CERTIFICADOS_EMAIL_USERNAME, settings.CERTIFICADOS_EMAIL_PASSWORD)
            m.select("INBOX")

            resp, items = m.search(None, 'FROM', '"Comodo Security Service"', 'UNSEEN', 'SUBJECT', '"Certificate"')
            items = items[0].split()

            for emailid in items:
                resp, data = m.fetch(emailid, "(RFC822)")
                email_body = data[0][1]
                mail = email.message_from_string(email_body)

                if mail.get_content_maintype() != 'multipart':
                    continue

                subject = mail.get('subject')
                log.info('Processando e-mail no certificatebox: {}'.format(subject))

                try:

                    emissao = self.get_emissao(subject)
                    emissao.emission_certificate = self.extract_certificate(mail)

                    dados_certificado = certificate_decode(emissao.emission_certificate)
                    emissao.voucher.ssl_valid_from = dados_certificado['validity']['not_before']
                    emissao.voucher.ssl_valid_to = dados_certificado['validity']['not_after']

                    emissao.emission_mail_attachment_path = self.get_attachment_path(mail)
                    emissao.emission_status = Emissao.STATUS_EMITIDO_SELO_PENDENTE
                    emissao.save()

                except (IndexError, AttributeError):
                    log.error('Recebeu e-mail fora do padrão (#{})'.format(subject), exc_info=1)
                except Emissao.DoesNotExist:
                    log.error('Recebeu e-mail com comodo order inexistente no banco (#{}) '.format(subject))
        finally:
            translation.activate(cur_language)

    def get_emissao(self, subject):
        from ecommerce.certificados.models import Emissao

        comodo_order = self.extract_comodo_order(subject)
        emissao = Emissao.objects.select_related('voucher').get(comodo_order=comodo_order)

        if emissao:
            log.info('Comodo Order: {}'.format(comodo_order))

        return emissao

    def get_attachment_path(self, mail):
        counter = 1
        path = None
        for part in mail.walk():
            if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                continue

            path, counter = self.extract_attachment(part, counter)

        if not path:
            log.error('Não conseguiu extrair o anexo')
            raise Exception('Não conseguiu extrair o anexo')

        return path

    def extract_comodo_order(self, subject):
        return re.match('.*ORDER #([0-9]+).*', subject).groups(0)[0]

    def extract_certificate(self, mail):
        text_content = str(list(mail.get_payload()[0].walk())[1])
        return re.match('.*(-----BEGIN (CERTIFICATE|PKCS7)-----.*-----END \2-----).*',
                        text_content, re.S).groups(0)[0]

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
            # cria as pastas de ano e mês
            os.makedirs(directory)

        timestamp = str(time()).replace('.', '')
        s = filename.split('.')
        filename = '.'.join(s[:-1])
        ext = s[-1]

        relative_path = os.path.join(ano, mes, '%s-%s.%s' % (filename, timestamp, ext))

        att_path = os.path.join(settings.CERTIFICADOS_EMAIL_PATH_ATTACHMENTS, relative_path)

        if not os.path.isfile(att_path):
            fp = open(att_path, 'wb')
            fp.write(part.get_payload(decode=True))
            fp.close()

        return relative_path, counter


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
        cur_language = translation.get_language()
        try:
            translation.activate('pt_BR')
            try:
                websites = self.extrai_websites()

                for line in ('basic', 'pro', 'prime'):
                    for website in websites[line]:
                        self.processa(line, website)
                self.post_do()
            except Exception as e:
                log.exception(self.error_message)
                raise e  # joga a exceção novamente para o django-cron tentar executar o job
                         # novamente depois de alguns minutos e enviar o email de aviso
        finally:
            translation.activate(cur_language)

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
                    websites[voucher.ssl_line].update((d, voucher.customer_cnpj, voucher.customer_companyname)
                                                      for d in voucher.emissao.get_lista_dominios())
                else:
                    log.warning('voucher multi-dominio sem urls #%s' % voucher.pk)

            if voucher.ssl_product == Voucher.PRODUTO_SAN_UCC:
                websites[voucher.ssl_line].add((voucher.emissao.emission_url, voucher.customer_cnpj, voucher.customer_companyname))

        return websites

    def processa(self, line, website):
        url, cnpj, razaosocial = website
        requests.post('%s/api/v1/ativar/%s/' % (settings.SEALS_SERVER_URL, line), {
            'username': settings.SEALS_USERNAME,
            'password': settings.SEALS_PASSWORD,
            'websites': url,
            'cnpj': cnpj,
            'razaosocial': razaosocial,
        })

    def processa_ativado(self, voucher):
        self.atualiza_contrato(voucher, 'valido')
        self.envia_email_cliente(voucher)

    def atualiza_contrato(self, voucher, status):
        try:
            client = CRMClient()
            with open(voucher.emissao.emission_mail_attachment_path, 'rb') as certificate_file:
                dominio = voucher.emissao.emission_url
                start_date = voucher.ssl_valid_from
                end_date = voucher.ssl_valid_to
                seal_html = voucher.get_seal_html
                client.atualizar_contrato(voucher.crm_hash, status, voucher.comodo_order, dominio, start_date, end_date,
                                          seal_html, certificate_file)
        except Exception as e:
            log.exception('Ocorreu um erro ao atualizar o contrato do voucher #%s para o status <%s>' % (voucher.crm_hash, status))
            self.envia_email_suporte(voucher, status)

    def envia_email_cliente(self, voucher):
        User = get_user_model()
        emissao = voucher.emissao
        try:
            user = User.objects.get(username=voucher.customer_cnpj)
            subject = '[TrustSign] Seu Novo Certificado'
            template = 'customer/emails/envio_certificado.html'
            context = {
                'voucher': voucher,
                'site': get_current_site(None),
            }
            email_cliente = emissao.emission_publickey_sendto if emissao.emission_publickey_sendto else user.email
            msg = get_template_email([email_cliente], subject, template, context)
            msg.attach_file(os.path.join(settings.CERTIFICADOS_EMAIL_PATH_ATTACHMENTS, emissao.emission_mail_attachment_path))
            msg.send()
        except User.DoesNotExist:
            log.warning('Emissão concluída de um CNPJ sem usuário cadastrado: {}'.format(voucher.customer_cnpj))

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

    def processa(self, line, website):
        url, cnpj, razaosocial = website
        requests.post('%s/api/v1/desativar/%s/' % (settings.SEALS_SERVER_URL, line), {
            'username': settings.SEALS_USERNAME,
            'password': settings.SEALS_PASSWORD,
            'websites': url,
            'cnpj': cnpj,
            'razaosocial': razaosocial,
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