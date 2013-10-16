from decimal import Decimal
from mezzanine.pages.page_processors import processor_for
from portal.products.models import Product
from django.db import connection

@processor_for(Product)
def ferramentas_processor(request, page):

    sql = '''
    SELECT p.upc, p.product_line, p.product_term, s.price_excl_tax
    FROM
       catalogue_product p
    inner join partner_stockrecord s
        on s.product_id = p.id
    where p.product_code = %s'''

    cursor = connection.cursor()
    cursor.execute(sql, [page.product.product_code])

    data = {
        'product_code': page.product.product_code,
        'precos': {
            'basic': {
                'term1year': {},
                'term2years': {},
                'term3years': {},
            },
            'pro': {
                'term1year': {},
                'term2years': {},
                'term3years': {},
            },
            'prime': {
                'term1year': {},
                'term2years': {},
                'term3years': {},
            }
        }
    }

    for upc, product_line, product_term, price in cursor.fetchall():
        price = price.quantize(Decimal('0.01'))
        x = data['precos'][product_line]['term%s' % product_term]
        x['price_tpl'] = str(price).split('.')
        x['price'] = price

    for line in ('basic', 'pro', 'prime'):
        data_line = data.setdefault('precos', {})[line]
        data_line.setdefault('term1year', {})['discount'] = 0
        preco_1ano = data_line.get('term1year', {}).get('price', 0)
        if preco_1ano > 0:
            data_line['term2years']['discount'] = int((1 - data_line.get('term2years', {}).get('price', 0) / (2 * preco_1ano)) * 100)
            data_line['term3years']['discount'] = int((1 - data_line.get('term3years', {}).get('price', 0) / (3 * preco_1ano)) * 100)

    return data