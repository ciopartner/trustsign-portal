# coding=utf-8
from __future__ import unicode_literals
import json
import os
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from portal.certificados.models import Emissao, Voucher
from portal.certificados.tests import CSR_SAN, CSR_SSL, CSR_WILDCARD, CAMPOS_GET_VOUCHER_DATA, CSR_MDC


class VoucherAPIViewTestCase(TestCase):

    fixtures = ['test-users.json', 'test-vouchers.json']

    def test_get_voucher_data(self):
        r = self.client.get(reverse('api_get_voucher_data'), {
            'crm_hash': 'test-SSL-emitido',
            'username': 'admin',
            'password': 'admin'
        })

        self.assertEquals(r.status_code, 200, 'Status Code != 200')

        data = json.loads(r.content)

        for campo in CAMPOS_GET_VOUCHER_DATA:
            d = data
            for c in campo.split('/'):
                self.assertIn(c, d, 'não retornou o campo: %s' % campo)
                d = d[c]
        data_product = data['product']
        self.assertEquals(data.get('crm_hash'), 'test-SSL-emitido')
        self.assertIn(data_product['ssl_line'].lower(), ('basico', 'pro', 'prime'))
        self.assertIn(data_product['ssl_term'].lower(), ('1 ano', '2 anos', '3 anos'))
        self.assertEquals(data_product['ssl_product'].lower(), 'ssl')

    def test_create_voucher(self):
        r = self.client.post(reverse('api_ssl_voucher_create'), {
            'username': 'admin',
            'password': 'admin',
            'crm_hash': 'testando-create',
            'ssl_code': '100010',
            'ssl_product': 'ssl',
            'ssl_line': 'basic',
            'ssl_term': '1year',
            'order_date': '13/10/2013 14:35',
            'order_channel': 'inside-sales',
            'order_item_value': '200.99',
            'customer_companyname': 'Empresa de Testes',
            'customer_cnpj': '99.913.392/0001-93',
            'customer_address1': 'rua de testes',
            'customer_city': 'São Paulo',
            'customer_state': 'SP',
            'customer_country': 'BR',
            'customer_zip': '04050-000'
        })

        data = json.loads(r.content)
        if r.status_code != 200:
            if r.status_code == 400:
                msg = '; '.join([e['message'] for e in data['errors']])
            else:
                msg = 'Status code != 200'
            self.fail(msg.encode('utf8'))

        try:
            Voucher.objects.get(crm_hash='testando-create')
        except Voucher.DoesNotExist:
            self.fail('não criou o voucher')

    def test_cancel_voucher(self):
        r = self.client.post(reverse('api_ssl_voucher_cancel'), {
            'username': 'admin',
            'password': 'admin',
            'crm_hash': 'test-MDC',
            'customer_cnpj': '51.813.518/0001-56',
            'order_cancel_reason': 'Testando'
        })

        data = json.loads(r.content)
        if r.status_code != 200:
            if r.status_code == 400:
                msg = '; '.join([e['message'] for e in data['errors']])
            else:
                msg = 'Status code != 200'
            self.fail(msg.encode('utf8'))

        try:
            voucher = Voucher.objects.get(crm_hash='test-MDC')
        except Voucher.DoesNotExist:
            self.fail('não criou o voucher')

        self.assertIsNotNone(voucher.order_canceled_date, 'Não setou o order_canceled_date')
        self.assertEqual(voucher.order_canceled_reason, 'Testando')

    def test_csr_url_validate_mdc(self):
        r = self.client.post(reverse('api_ssl_validate_url_csr'), {
            'crm_hash': 'test-MDC',
            'username': 'admin',
            'password': 'admin',
            'emission_url': 'paulo.trustsign.com.br',
            'emission_csr': CSR_MDC
        })
        self.assertEquals(r.status_code, 200)

        data = json.loads(r.content)

        self.assertIn('required_fields', data)
        self.assertIn('server_list', data)
        self.assertIn('ssl_urls', data)
        self.assertIn('server_list', data)

        self.assertEqual(len(data['ssl_urls']), 4)

        dominios_restantes = ['webmail.grupocrm.com.br', 'autodiscover.grupocrm.com.br', 'imap.grupocrm.com.br',
                              'mobile.grupocrm.com.br']

        for url in data['ssl_urls']:
            self.assertIn(url['url'], dominios_restantes)
            dominios_restantes.remove(url['url'])

        self.assertEqual(len(dominios_restantes), 0)

    def test_ssl_apply_mdc(self):
        r = self.client.post(reverse('api_ssl_apply'), {
            'username': 'admin',
            'password': 'admin',
            'crm_hash': 'test-MDC',
            'emission_urls': 'webmail.grupocrm.com.br autodiscover.grupocrm.com.br imap.grupocrm.com.br',
            'emission_csr': CSR_MDC,
            'emission_server_type': 1,
            'emission_dcv_emails': 'admin@grupocrm.com.br admin@grupocrm.com.br admin@grupocrm.com.br',
            'emission_publickey_sendto': 'admin@grupocrm.com.br',
            'emission_assignment_letter': open(os.path.join(settings.PROJECT_ROOT, 'portal', 'static', 'robots.txt'), 'r')
        })

        #self.assertEquals(r.status_code, 200)

        data = json.loads(r.content)
        self.assertEqual(data, {})
        try:
            emissao = Emissao.objects.get(crm_hash='test-MDC')
        except Emissao.DoesNotExist:
            self.fail('Não criou a emissão')

        self.assertEqual(emissao.emission_urls, 'webmail.grupocrm.com.br autodiscover.grupocrm.com.br imap.grupocrm.com.br')

    def test_ssl_apply_smime(self):
        r = self.client.post(reverse('api_ssl_apply'), {
            'username': 'admin',
            'password': 'admin',
            'crm_hash': 'test-SMIME',
            'emission_revoke_password': 'password',
            'emission_id': open(os.path.join(settings.PROJECT_ROOT, 'portal', 'static', 'robots.txt'), 'r')
        })

        #self.assertEquals(r.status_code, 200)

        data = json.loads(r.content)
        self.assertEqual(data, {})
        try:
            emissao = Emissao.objects.get(crm_hash='test-SMIME')
        except Emissao.DoesNotExist:
            self.fail('Não criou a emissão')

        self.assertEqual(emissao.emission_revoke_password, 'password')
        self.assertIsNotNone(emissao.emission_id)