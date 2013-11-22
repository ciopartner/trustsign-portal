# coding=utf-8
from logging import getLogger
from django.contrib.auth import get_user_model
from django.contrib.sites.models import get_current_site
from django_cron import CronJobBase, Schedule
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
        Order = get_class('order.models', 'Order')
        for order in Order.objects.filter(status='Pago')[:20]:
            self.send_order_to_crm(order)

            order.set_status('Em Processamento')
            for line in order.lines.all():
                line.set_status('Em Processamento')
            log.info('Order #%s: alterado status para Em processamento' % order.number)


    def send_email(self, order):
        try:
            subject = 'Processo de Emissão Liberado'
            template = 'customer/emails/pedido_concluido.html'
            context = {
                'order': order,
                'site': get_current_site(None),
            }
            send_template_email([order.user.email], subject, template, context)
        except User.DoesNotExist:
            log.warning('Emissão liberada sem usuário da order #{}'.format(order.number))