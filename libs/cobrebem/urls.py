# -*- coding: utf-8 -*-
from django.conf.urls.default import *
from django.conf.urls import patterns, url

urlpatterns = patterns('cobrebem.views',

    url(r'^', 'index', name='index'),

)
