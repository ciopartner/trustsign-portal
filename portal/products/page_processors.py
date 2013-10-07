from decimal import Decimal
from mezzanine.pages.page_processors import processor_for
from portal.products.models import Product


@processor_for(Product)
def ferramentas_processor(request, page):


    return {
        'product_code': 'ssl',
        'precos': {
            'basic': {
                'term1year': Decimal('10.20'),
                'term2years': Decimal('130.20'),
                'term3years': Decimal('1920.20')
            },
            'pro': {
                'term1year': Decimal('140.20'),
                'term2years': Decimal('210.20'),
                'term3years': Decimal('2510.20')
            },
            'prime': {
                'term1year': Decimal('610.20'),
                'term2years': Decimal('1110.20'),
                'term3years': Decimal('9140.20')
            }
        }
    }