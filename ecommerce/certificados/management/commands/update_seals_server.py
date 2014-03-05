# coding: utf-8
from __future__ import unicode_literals
from logging import getLogger
from django.conf import settings
from django.core.management import BaseCommand
from django.utils.timezone import now
import requests
from ecommerce.certificados.models import Emissao, Voucher
from ecommerce.certificados.validations import is_nome_interno

log = getLogger('ecommerce.certificados.commands')


class Command(BaseCommand):

    def handle(self, *args, **options):
        websites = {
            'basic': set(),
            'pro': set(),
            'prime': set(),
        }

        for emissao in Emissao.objects.select_related('voucher').filter(
            emission_status__in=(Emissao.STATUS_EMITIDO,Emissao.STATUS_REEMITIDO),
            voucher__ssl_valid_to__gte=now()
        ):
            voucher = emissao.voucher
            if emissao.voucher.ssl_product in (Voucher.PRODUTO_MDC, Voucher.PRODUTO_EV_MDC, Voucher.PRODUTO_SAN_UCC):
                if emissao.emission_urls:
                    websites[voucher.ssl_line].update((d, voucher.customer_cnpj, voucher.customer_companyname)
                                                      for d in emissao.get_lista_dominios()
                                                      if not is_nome_interno(d))
                else:
                    log.warning('voucher multi-dominio sem urls #%s' % voucher.pk)

                if emissao.voucher.ssl_product == Voucher.PRODUTO_SAN_UCC:
                    if not is_nome_interno(voucher.emissao.emission_url):
                        websites[voucher.ssl_line].add((voucher.emissao.emission_url,
                                                        voucher.customer_cnpj,
                                                        voucher.customer_companyname))

            else:
                if not is_nome_interno(voucher.emissao.emission_url):
                    websites[voucher.ssl_line].add((emissao.emission_url,
                                                    voucher.customer_cnpj,
                                                    voucher.customer_companyname))

        for line in ('basic', 'pro', 'prime'):
            for website in websites[line]:
                self.processa(line, website)

    def processa(self, line, website):
        url, cnpj, razaosocial = website

        log.info('Ativando selo: {} - {} -{}'.format(url, cnpj, razaosocial))
        response = requests.post('%s/api/v1/ativar/%s/' % (settings.SEALS_SERVER_URL, line), {
            'username': settings.SEALS_USERNAME,
            'password': settings.SEALS_PASSWORD,
            'websites': url,
            'cnpj': cnpj,
            'razaosocial': razaosocial,
        }, verify=False)

        if response.status_code != 200:
            log.error('Erro ao ativar o selo: {}'.format(response.text))
        else:
            log.info('Selo ativado com sucesso!')