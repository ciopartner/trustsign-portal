# coding=utf-8
from __future__ import unicode_literals
import json
from django.core.urlresolvers import reverse
from django.test import TestCase
from portal.certificados.tests import CSR_SAN, CSR_SSL, CSR_WILDCARD, CAMPOS_GET_VOUCHER_DATA


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