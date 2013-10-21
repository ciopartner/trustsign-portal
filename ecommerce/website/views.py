# coding=utf-8
from __future__ import unicode_literals
from django.core.cache import cache
from django.forms import ValidationError
from django.http import Http404
from localflavor.br.forms import BRCNPJField
from oscar.apps.basket.views import BasketAddView
from oscar.apps.catalogue.models import Product
from ecommerce.website.forms import AdicionarProdutoForm
from libs import knu
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

    def render_to_response(self, context, **response_kwargs):
        if 'erro' in context:
            response_kwargs['status'] = 400
        return super(GetCNPJDataView, self).render_to_response(context, **response_kwargs)

    def get_cnpj_data(self, cnpj):
        try:
            BRCNPJField().clean(cnpj)
        except ValidationError:
            return {
                'erro': 'CNPJ inválido!'
            }
        data = cache.get('cnpj-%s' % cnpj)
        if data is None:
            # TODO: Descomentar para usar KNU para buscar os dados do CNPJ
            #r = knu.receitaCNPJ(cnpj)
            #if r.cod_erro != 0:
            #    log.warning('Erro na requisição da knu: (%d) %s' % (r.cod_erro, r.desc_erro))
            #    return {'erro': 'Erro interno'}
            #data = {
            #    'cnpj': cnpj,
            #    'razao_social': r.nome_empresarial,
            #    'logradouro': r.logradouro,
            #    'numero': r.numero,
            #    'complemento': r.complemento,
            #    'cep': r.cep,
            #    'bairro': r.bairro,
            #    'cidade': r.municipio,
            #    'uf': r.uf,
            #    'situacao_cadastral': r.situacao_cadastral,
            #    'knu_html': r.html
            #}

            data = {
                'cnpj': cnpj,
                'razao_social': 'CIO Partner',
                'logradouro': 'Av. Dr. Candido Motta Filho',
                'numero': '856',
                'complemento': '1º andar',
                'cep': '05351010',
                'bairro': 'Vila São Francisco',
                'cidade': 'São Paulo',
                'uf': 'SP',
                'situacao_cadastral': 'ativa',
                'knu_html': '<html></html>'
            }
            cache.set('cnpj-%s' % cnpj, data, 2592000)  # cache de 30 dias
        return data


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
        try:
            qs = Product.objects.filter(product_code=product_code)
            if line:
                qs = qs.filter(product_line=line)
            if term:
                qs = qs.filter(product_term=term)
            return qs.get().pk
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