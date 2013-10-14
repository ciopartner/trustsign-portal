# -*- coding: utf-8 -*-
from django.contrib import messages
from django import http
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView, View

from libs.cobrebem.facade import Facade

from oscar.apps.customer import views
from oscar.apps.payment.models import Source, Transaction
from oscar.apps.order.models import Order


class OrderCancelView(RedirectView):
    
    def get_redirect_url(self, **kwargs):        
        return reverse('customer:order', kwargs={'order_number':kwargs['order_number']})

    def get(self, request, *args, **kwargs):        
        result_order_cancel = self.do_order_cancel(request, *args, **kwargs)
        order = get_object_or_404(Order, number=kwargs['order_number'])
        if result_order_cancel.startswith("Cancelamento marcado para envio"):
            order.set_status("Cancelamento em processo")
        else:
            order.set_status("Cancelado")
        messages.success(request, result_order_cancel)
        response = super(OrderCancelView, self).get(request, *args, **kwargs)
        return response

    def do_order_cancel(self, request, *args, **kwargs):
        source = get_object_or_404(Source,order__number=kwargs['order_number'])
        facade = Facade()
        cobrebem_cancel_result = facade.cancel(source.reference)
        return cobrebem_cancel_result

class OrderCancelReturnView(View):
    
    def get(self, request, *args, **kwargs):            
        transaction = request.GET['Transacao']        
        order_number = request.GET['NumeroDocumento']
        result = request.GET['ResultadoSolicitacaoCancelamento']
        nsu = request.GET['NSUCancelamento']              
        if result.startswith("Cancelado"):            
            order = get_object_or_404(Order, number=order_number)
            order.set_status('Cancelado')                        
        return HttpResponse("OK")

    
