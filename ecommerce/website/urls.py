from django.conf.urls import patterns, url
from .views import GetCNPJDataView

urlpatterns = patterns(
    '',
    url(r'^ajax/get-cnpj-data/$', GetCNPJDataView.as_view()),
)