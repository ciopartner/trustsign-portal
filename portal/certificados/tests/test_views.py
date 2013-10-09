# coding=utf-8
from __future__ import unicode_literals
import json
from django.core.urlresolvers import reverse
from django.test import TestCase
from portal.certificados.tests import CSR_SAN, CSR_SSL, CSR_WILDCARD, CAMPOS_GET_VOUCHER_DATA, CSR_MDC


class VoucherAPIViewTestCase(TestCase):

    fixtures = ['test-users.json', 'test-vouchers.json']

    def test_get_voucher_data(self):
        r = self.client.get(reverse('api_get_voucher_data'), {'crm_hash': 'test-SSL-emitido',
                                                              'username': 'admin',
                                                              'password': 'admin'})

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

        self.assertEqual(len(data['ssl_urls']), 2)

        for url in data['ssl_urls']:
            self.assertIn(url['url'], ('paulo.trustsign.com.br', 'sthefane.trustsign.com.br'))
            if url['url'] == 'paulo.trustsign.com.br':
                self.assertTrue(url['primary'])