# coding=utf-8
import csv
from django.core.management import BaseCommand
from ecommerce.certificados.models import Voucher


class Command(BaseCommand):
    args = '<path_csvfile>'

    def handle(self, *args, **options):

        path_csvfile = args[0]
        i = 0

        with open(path_csvfile, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')

            for crm_hash, ssl_product, ssl_line, ssl_term, order_date, order_item_value, customer_cnpj, \
                customer_companyname, customer_address1, customer_address2, customer_address3, customer_address4, \
                    customer_zip, customer_city, customer_state in csvreader:

                Voucher.objects.create(
                    crm_hash=crm_hash,
                    customer_cnpj=customer_cnpj,
                    customer_companyname=customer_companyname,
                    customer_address1=customer_address1,
                    customer_address2=customer_address2,
                    customer_address3=customer_address3,
                    customer_address4=customer_address4,
                    customer_zip=customer_zip,
                    customer_city=customer_city,
                    customer_state=customer_state,
                    customer_country='BR',
                    customer_registration_status=True,

                    ssl_product=ssl_product,
                    ssl_line=ssl_line,
                    ssl_term=ssl_term,

                    order_date=order_date,
                    order_item_value=order_item_value,
                    order_channel=Voucher.ORDERCHANNEL_INSIDE_SALES,
                )

                i += 1

        self.stdout.write('Importou {} registro(s) com sucesso'.format(i))