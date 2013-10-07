from django.forms import ChoiceField
from oscar.apps.basket.forms import AddToBasketForm
from portal.certificados.models import Voucher


class AdicionarProdutoForm(AddToBasketForm):
    line = ChoiceField(choices=Voucher.LINHA_CHOICES)
    term = ChoiceField(choices=Voucher.VALIDADE_CHOICES)