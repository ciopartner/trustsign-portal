# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from oscar.apps.customer import app

from ecommerce.apps.customer import views


class CustomerApplication(app.CustomerApplication):        
    order_cancel_view = views.OrderCancelView    
    order_cancel_return_view = views.OrderCancelReturnView
    profile_update_view = views.ProfileUpdateView
    change_password_view = views.ChangePasswordView

    def get_urls(self): 
        urlpatterns = super(CustomerApplication, self).get_urls()        
        urlpatterns += patterns(
            '',
            url(r'^orders/(?P<order_number>[\w-]+)/cancel/$',
                login_required(self.order_cancel_view.as_view()),
                name='order-cancel'),            
            url(r'^orders/cancel/return/$',
                self.order_cancel_return_view.as_view(),
                name='order-cancel-return'),   
        )
             
        return self.post_process_urls(urlpatterns)

application = CustomerApplication()
