# coding=utf-8
from logging import getLogger
from django_cron import CronJobBase, Schedule
from oscar.core.loading import get_class
from libs.crm.mixins import OscarToCRMMixin

log = getLogger('ecommerce.website.crons')


class EnviaOrdersCRMCronJob(CronJobBase, OscarToCRMMixin):
    """
    Envia para a comodo as emissões com status aguardando envio comodo.
    """
    RUN_EVERY_MINS = 5

    code = 'ecommerce.envia_orders_crm'
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)

    def do(self):
        Order = get_class('order.models', 'Order')
        for order in Order.objects.filter(status='Pago')[:20]:
            self.send_order_to_crm(order)

            order.set_status('Em Processamento')
            for line in order.lines.all():
                line.set_status('Em Processamento')
            log.info('Order #%s: alterado status para Em processamento' % order.pk)