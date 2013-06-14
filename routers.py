# -*- coding: utf-8 -*-
"""
Roteador de Banco de Dados:
Banco commom => utilizado por users, groups, permissions, sessions

Colocar na primeira linha do middleware para entrar em operação.
Por questões de um bug no django, o mesmo banco de dados está sendo utilizado.
"""

import threading

# Object to hold request data
request_cfg = threading.local()


class RouterMiddleware(object):
    """
    Set a flag if we are accessing Django admin to
    prevent database rerouting for the auth model.
    Remove the flag once the request has been processed.
    """

    def process_view(self, request, view_func, args, kwargs):
        if request.path.startswith('/admin'):
            request_cfg.admin = True

    def process_response(self, request, response):
        if hasattr(request_cfg, 'admin'):
            del request_cfg.admin
        return response


class UserSessionRouter(object):
    """
    Redirect database IO for the auth and sessions
    models to OldWebsite.com.
    """

    # Apps para o banco 'common'
    APPS = ['auth', 'accounts', 'sessions', 'app_label', 'sites', 'permission', 'contenttypes', 'auth_permission']

    def db_for_read(self, model, **hints):
        if not hasattr(request_cfg, 'admin'):
            if model._meta.app_label in self.APPS:
                return 'common'
        return None

    def db_for_write(self, model, **hints):
        if not hasattr(request_cfg, 'admin'):
            if model._meta.app_label in self.APPS:
                return 'common'
        return None