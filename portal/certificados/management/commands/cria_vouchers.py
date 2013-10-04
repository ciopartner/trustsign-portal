# coding=utf-8
from copy import copy
from django.core.management import BaseCommand
from portal.certificados.models import Voucher


class Command(BaseCommand):
    args = '<qtd_vouchers>'

    def handle(self, *args, **options):
        qtd_vouchers = int(args[0]) if len(args) > 0 else 50

        for crm_hash in ('SSL', 'WILDCARD', 'MDC', 'SAN', 'EV', 'EV-MDC', 'JRE', 'CODE-SIGNING', 'SMIME'):
            voucher_base = Voucher.objects.get(crm_hash=crm_hash)

            for i in range(qtd_vouchers):
                try:
                    # remove se já existir
                    voucher = Voucher.objects.get(crm_hash='%s%s' % (crm_hash, i))
                    voucher.delete()
                except Voucher.DoesNotExist:
                    pass

                voucher = copy(voucher_base)
                voucher.id = None
                voucher.crm_hash += str(i)
                voucher.save()

        self.stdout.write('Criou %d vouchers de cada tipo"' % qtd_vouchers)