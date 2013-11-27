# coding=utf-8
from __future__ import unicode_literals
from django.forms import ValidationError
from django.http import Http404
from django.views.generic import RedirectView
from localflavor.br.forms import BRCNPJField
from oscar.apps.basket.views import BasketAddView
from oscar.apps.catalogue.models import Product
from ecommerce.website.forms import AdicionarProdutoForm
from ecommerce.website.utils import get_dados_empresa
from portal.portal.utils import JSONView, JSONFormView
from logging import getLogger

log = getLogger('ecommerce.website.views')


class GetCNPJDataView(JSONView):
    """
    Retorna dados da empresa de acordo com o CNPJ informado por ajax
    """

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        cnpj = self.request.POST.get('cnpj')
        if cnpj:
            return self.get_cnpj_data(cnpj)
        return {'erro': 'cnpj não encontrado'}

    def get_cnpj_data(self, cnpj):
        try:
            BRCNPJField().clean(cnpj)
        except ValidationError:
            return {
                'erro': 'CNPJ inválido!'
            }

        return get_dados_empresa(cnpj)


class AdicionarProdutoView(BasketAddView, JSONFormView):
    """
    Adiciona produtos ao carrinho por ajax
    """
    form_class = AdicionarProdutoForm

    def get(self, request, *args, **kwargs):
        raise Http404()

    def get_form_kwargs(self):
        kwargs = {'initial': self.get_initial()}
        data = self.request.POST.copy()
        data['product_id'] = self.get_product_id(
            data.get('product_code', ''),
            data.get('line', ''),
            data.get('term', '')
        )

        product_select_form = self.product_select_form_class(data)

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': data,
                'files': self.request.FILES,
                'request': self.request,
                'instance': product_select_form.cleaned_data['product_id'] if product_select_form.is_valid() else None
            })

        return kwargs

    def get_product_id(self, product_code, line=None, term=None):
        """
        retorna o id do produto no oscar usando o code, line e term, para usar o metodo padrão de adicionar na basket
        """
        try:
            produtos = Product.objects.filter(
                attribute_values__attribute__code='ssl_code',
                attribute_values__value_option__option=product_code
            )

            for produto in produtos:
                product_line = str(produto.attr.ssl_line)
                product_term = str(produto.attr.ssl_term)
                if line:
                    if line != product_line or (term and term != product_term):  # se line ou term forem diferentes vai pro proximo
                        continue
                    return produto.pk
                if term and term != product_term:
                    continue
                return produto.pk

            return -1  # não encontrou o produto com a line e term desejados,
            # retorna -1 para falhar na validação do oscar
        except Product.DoesNotExist:
            return -1

    def form_valid(self, form):
        self.request.basket.add_product(
            form.instance, form.cleaned_data['quantity'],
            form.cleaned_options())
        return self.render_to_response({
            'ok': True
        })

    def form_invalid(self, form):
        return self.render_to_response(form.errors, status=400)


class EsvaziarCarrinhoView(RedirectView):

    permanent = False
    url = '/ecommerce/basket/'

    def get(self, *args, **kwargs):
        try:
            self.request.basket.flush()
        except:
            pass
        return super(EsvaziarCarrinhoView, self).get(*args, **kwargs)