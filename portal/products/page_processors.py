from decimal import Decimal
from mezzanine.pages.page_processors import processor_for
from portal.products.models import Product
from django.db import connection


def split1000(s, sep='.'):
    return s if len(s) <= 3 else split1000(s[:-3], sep) + sep + s[-3:]


@processor_for(Product)
def product_processor(request, page):

    #sql = '''
    #SELECT p.upc, p.product_line, p.product_term, s.price_excl_tax
    #FROM
    #   catalogue_product p
    #inner join partner_stockrecord s
    #    on s.product_id = p.id
    #where p.product_code = %s'''

    sql = '''
        select cp.upc, cao_line.option, cao_term.option, s.price_excl_tax from catalogue_product as cp
           inner join catalogue_productattribute as cpa on cp.product_class_id =  cpa.product_class_id
           inner join catalogue_productattributevalue as cpav on cpa.id = cpav.attribute_id and cp.id = cpav.product_id
           inner join catalogue_attributeoption as cao on cao.id = cpav.value_option_id

           inner join catalogue_productattribute as cpa_line on cp.product_class_id =  cpa_line.product_class_id
           inner join catalogue_productattributevalue as cpav_line on cpa_line.id = cpav_line.attribute_id and cp.id = cpav_line.product_id
           inner join catalogue_attributeoption as cao_line on cao_line.id = cpav_line.value_option_id

           inner join catalogue_productattribute as cpa_term on cp.product_class_id =  cpa_term.product_class_id
           inner join catalogue_productattributevalue as cpav_term on cpa_term.id = cpav_term.attribute_id and cp.id = cpav_term.product_id
           inner join catalogue_attributeoption as cao_term on cao_term.id = cpav_term.value_option_id

           inner join partner_stockrecord s  on s.product_id = cp.id
        where cpa.code='ssl_code' and cpa_line.code='ssl_line' and cpa_term.code='ssl_term' and cao.option=%s
    '''

    cursor = connection.cursor()
    cursor.execute(sql, [page.product.product_code])

    data = {
        'product_code': page.product.product_code,
        'precos': {
            'basic': {
                'termsubscription_1m': {},
                'term1year': {},
                'term2years': {},
                'term3years': {},
            },
            'pro': {
                'termsubscription_1m': {},
                'term1year': {},
                'term2years': {},
                'term3years': {},
            },
            'prime': {
                'termsubscription_1m': {},
                'term1year': {},
                'term2years': {},
                'term3years': {},
            },
            'trial': {
                'termtrial': {}
            },
            'na': {
                'termsubscription_1m': {},
                'term1year': {},
                'term2years': {},
                'term3years': {}
            }
        }
    }

    for upc, product_line, product_term, price in cursor.fetchall():
        if price is None:
            price = Decimal(0)

        price = price.quantize(Decimal('0.01'))
        x = data['precos'][product_line]['term%s' % product_term]
        num, dec = str(price).split('.')
        x['price_tpl'] = split1000(num), dec
        x['price'] = price

    for line in ('basic', 'pro', 'prime', 'na'):

        data_line = data.setdefault('precos', {})[line]
        data_line.setdefault('term1year', {})['discount'] = 0
        preco_1ano = data_line.get('term1year', {}).get('price', 0)

        if preco_1ano > 0:
            data_line['term2years']['discount'] = int((1 - data_line.get('term2years', {}).get('price', 0) / (2 * preco_1ano)) * 100)
            data_line['term3years']['discount'] = int((1 - data_line.get('term3years', {}).get('price', 0) / (3 * preco_1ano)) * 100)

    return data