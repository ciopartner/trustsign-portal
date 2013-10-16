from decimal import Decimal
from mezzanine.pages.page_processors import processor_for
from portal.products.models import Product
from django.db import connection

@processor_for(Product)
def ferramentas_processor(request, page):

    sql = '''
    SELECT * FROM
       catalogue_product
    inner join partner_stockrecord
        on partner_stockrecord.product_id = catalogue_product.id where catalogue_product.product_code = %s'''

    cursor = connection.cursor()
    cursor.execute(sql, [page.product.product_code])

    for row in cursor.fetchall():
        print(row)

    return {
        'product_code': 'ssl',
        'precos': {
            'basic': {
                'term1year': [['1000','20'],['2000','40'],['3000','60']],
                'term2years': ['1500','20'],
                'term3years': ['2250','20']
            },
            'pro': {
                'term1year': [['1340','20'],['2680','40'],['4020','60']],
                'term2years': ['2310','20'],
                'term3years': ['2510','20']
            },
            'prime': {
                'term1year': [['6010','20'],['12020','40'],['36030','60']],
                'term2years':['11010','20'],
                'term3years': ['21040','20']
            }
        }
    }