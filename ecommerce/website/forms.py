from django.forms import ChoiceField
from oscar.apps.basket.forms import AddToBasketForm
from ecommerce.certificados.models import Voucher


class AdicionarProdutoForm(AddToBasketForm):
    line = ChoiceField(choices=Voucher.LINHA_CHOICES + (('na', 'Sem linha'),))
    term = ChoiceField(choices=Voucher.VALIDADE_CHOICES)