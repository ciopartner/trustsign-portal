# coding=utf-8
from __future__ import unicode_literals
from logging import getLogger
from django.contrib.auth import get_user_model
from django.contrib.sites.models import get_current_site
from django.utils import translation
from django_cron import CronJobBase, Schedule
from oscar.apps.order.exceptions import InvalidLineStatus
from oscar.core.loading import get_class
from ecommerce.website.utils import send_template_email
from libs.crm.mixins import OscarToCRMMixin

User = get_user_model()
log = getLogger('ecommerce.website.crons')


class EnviaOrdersCRMCronJob(CronJobBase, OscarToCRMMixin):
    """
    Envia para a comodo as emissões com status aguardando envio comodo.
    """
    RUN_EVERY_MINS = 1

    code = 'ecommerce.envia_orders_crm'
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)

    def do(self):
        cur_language = translation.get_language()
        try:
            translation.activate('pt_BR')
            Order = get_class('order.models', 'Order')
            for order in Order.objects.filter(status='Pago')[:20]:
                self.send_order_to_crm(order)

                order.set_status('Em Processamento')

                for line in order.lines.all():
                    try:
                        line.set_status('Em Processamento')
                    except InvalidLineStatus:
                        log.warning('Order #{}: erro ao alterar o status da linha para Em Processamento'.format(order.number))

                self.send_email(order)

                log.info('Order #{}: alterado status para Em processamento'.format(order.number))
        finally:
            translation.activate(cur_language)

    def send_email(self, order):
        try:
            subject = '[TrustSign] Processo de Emissão Liberado'
            template = 'customer/emails/pedido_concluido.html'
            context = {
                'order': order,
                'site': get_current_site(None),
            }
            log.info('Enviando e-mail de Processo de Emissão Liberado para o pedido #{}'.format(order.number))
            send_template_email([order.user.email], subject, template, context)
        except User.DoesNotExist:
            log.warning('Emissão liberada sem usuário da order #{}'.format(order.number))