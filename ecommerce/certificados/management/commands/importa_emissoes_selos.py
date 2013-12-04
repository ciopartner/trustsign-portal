# coding=utf-8
import csv
from django.core.management import BaseCommand
from ecommerce.certificados.models import Voucher, Emissao


class Command(BaseCommand):
    args = '<path_csvfile>'

    def handle(self, *args, **options):

        path_csvfile = args[0]
        i = 0

        with open(path_csvfile, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for crm_hash in csvreader:
                try:
                    voucher = Voucher.objects.get(crm_hash=crm_hash)
                    Emissao.objects.create(
                        voucher=voucher,
                        crm_hash=crm_hash,
                    )
                    i += 1
                except Voucher.DoesNotExist:
                    self.stderr.write('Não encontrou o voucher com crm_hash: {}'.format(crm_hash))

        self.stdout.write('Importou {} registro(s) com sucesso'.format(i))