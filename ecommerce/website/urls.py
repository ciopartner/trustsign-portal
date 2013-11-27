from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt
from ecommerce.apps.checkout.akatus.views import StatusChangedView
from .views import GetCNPJDataView, AdicionarProdutoView, EsvaziarCarrinhoView

urlpatterns = patterns(
    '',
    url(r'^ajax/get-cnpj-data/$', GetCNPJDataView.as_view()),
    url(r'^ajax/adicionar-produto/$', csrf_exempt(AdicionarProdutoView.as_view())),
    url(r'^esvaziar-carrinho/$', EsvaziarCarrinhoView.as_view(), name='esvaziar-carrinho'),
    url(r'^api/v1/atualiza-status-pagto/$', csrf_exempt(StatusChangedView.as_view())),
)