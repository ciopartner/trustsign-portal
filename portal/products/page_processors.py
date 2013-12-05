from decimal import Decimal
from mezzanine.pages.page_processors import processor_for
from portal.products.models import Product
from django.db import connection


def split1000(s, sep='.'):
    return s if len(s) <= 3 else split1000(s[:-3], sep) + sep + s[-3:]


def split_ponto(price):
        num, dec = str(price).split('.')
        return split1000(num), dec


@processor_for(Product)
def product_processor(request, page):

    sql = '''
        select cp.upc, cao_line.option, cao_term.option, s.price_excl_tax, oo.id, oo.label, ooi.price_discount from catalogue_product as cp
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
           left join offer_fixedpriceofferitem ooi on ooi.product_id=cp.id
           left join offer_fixedpriceoffer oo on oo.id=ooi.offer_id and oo.status='Open' and oo.start_datetime < DATETIME('now') and oo.end_datetime > DATETIME('now')
        where cpa.code='ssl_code' and cpa_line.code='ssl_line' and cpa_term.code='ssl_term' and cao.option=%s
    '''

    cursor = connection.cursor()
    cursor.execute(sql, [page.product.product_code])

    data = {
        'product_code': page.product.product_code,
        'additional_product_code': page.product.additional_product_code,
        'show_discount': True,
        'precos': {
            'basic': {
                'termsubscription_1m': {},
                'termtrial': {},
                'term1year': {},
                'term2years': {},
                'term3years': {},
            },
            'pro': {
                'termsubscription_1m': {},
                'termtrial': {},
                'term1year': {},
                'term2years': {},
                'term3years': {},
            },
            'prime': {
                'termsubscription_1m': {},
                'termtrial': {},
                'term1year': {},
                'term2years': {},
                'term3years': {},
            },
            'na': {
                'termsubscription_1m': {},
                'termtrial': {},
                'term1year': {},
                'term2years': {},
                'term3years': {}
            }
        }
    }

    for upc, product_line, product_term, price, offer_id, offer_label, price_discount in cursor.fetchall():
        print upc, product_line, product_term, price, offer_id, offer_label, price_discount
        if price is None:
            price = Decimal(0)

        if offer_id is not None and price_discount is not None:
            price_regular = price
            price_regular = price_regular.quantize(Decimal('0.01'))
            price = price_discount
        else:
            price_regular = None

        price = price.quantize(Decimal('0.01'))

        if price_regular is not None:
            data['show_discount'] = False

        data['precos'][product_line]['term%s' % product_term].update({
            'price_tpl': split_ponto(price),
            'price': price,
            'has_discount': price_regular is not None,
            'price_regular': price_regular,
            'price_regular_tpl': split_ponto(price_regular) if price_regular else None,
            'label': offer_label,
        })

    for line in ('basic', 'pro', 'prime', 'na'):

        data_line = data.setdefault('precos', {})[line]
        data_line.setdefault('term1year', {})['discount'] = 0
        preco_1ano = data_line.get('term1year', {}).get('price', 0)

        if preco_1ano > 0:
            data_line['term2years']['discount'] = int(
                (1 - data_line.get('term2years', {}).get('price', 0) / (2 * preco_1ano)) * 100)
            data_line['term3years']['discount'] = int(
                (1 - data_line.get('term3years', {}).get('price', 0) / (3 * preco_1ano)) * 100)

    cursor = connection.cursor()
    cursor.execute(sql, [page.product.additional_product_code])

    for upc, product_line, product_term, price, offer_id, offer_label, price_discount in cursor.fetchall():
        if price is None:
            price = Decimal(0)

        if offer_id is not None and price_discount is not None:
            price_regular = price
            price_regular = price_regular.quantize(Decimal('0.01'))
            price = price_discount
        else:
            price_regular = None

        price = price.quantize(Decimal('0.01'))

        x = data.setdefault('adicional', {})\
            .setdefault('precos', {})\
            .setdefault(product_line, {})\
            .setdefault('term%s' % product_term, {})

        if price_regular is not None:
            data['show_discount'] = False

        x.update({
            'price_tpl': split_ponto(price),
            'price': price,
            'has_discount': price_regular is not None,
            'price_regular': price_regular,
            'price_regular_tpl': split_ponto(price_regular) if price_regular else None,
            'label': offer_label,
        })


    return data