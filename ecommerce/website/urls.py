from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt
from .views import GetCNPJDataView, AdicionarProdutoView

urlpatterns = patterns(
    '',
    url(r'^ajax/get-cnpj-data/$', GetCNPJDataView.as_view()),
    url(r'^ajax/adicionar-produto/$', csrf_exempt(AdicionarProdutoView.as_view())),
)