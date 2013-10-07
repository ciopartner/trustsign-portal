from django.conf.urls import patterns, url
from .views import GetCNPJDataView, AdicionarProdutoView

urlpatterns = patterns(
    '',
    url(r'^ajax/get-cnpj-data/$', GetCNPJDataView.as_view()),
    url(r'^ajax/adicionar-produto/$', AdicionarProdutoView.as_view()),
)