from decimal import Decimal
from mezzanine.pages.page_processors import processor_for
from portal.products.models import Product


@processor_for(Product)
def ferramentas_processor(request, page):


    return {
        'product_code': 'ssl',
        'precos': {
            'basic': {
                '1year': Decimal('10.20'),
                '2years': Decimal('130.20'),
                '3years': Decimal('1920.20')
            },
            'pro': {
                '1year': Decimal('140.20'),
                '2years': Decimal('210.20'),
                '3years': Decimal('2510.20')
            },
            'prime': {
                '1year': Decimal('610.20'),
                '2years': Decimal('1110.20'),
                '3years': Decimal('9140.20')
            }
        }
    }