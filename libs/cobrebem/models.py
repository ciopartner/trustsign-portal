# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _


class CobreBemTransaction(models.Model):
    
    order_number = models.CharField(_(u'Número do pedido'), max_length=128)
    method = models.CharField(_(u'Método'), max_length=30)

