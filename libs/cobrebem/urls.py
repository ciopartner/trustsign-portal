# -*- coding: utf-8 -*-
from django.conf.urls.default import *

urlpatterns = patterns('cobrebem.views',

    url(r'^', 'index', name='index'),

)
