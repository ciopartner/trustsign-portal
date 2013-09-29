# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class UserPasswordAuthentication(BaseAuthentication):
    def authenticate(self, request):
        if request.method == 'GET':
            username = request.GET.get('username')
            password = request.GET.get('password')
        else:
            username = request.DATA.get('username')
            password = request.DATA.get('password')

        if not username:
            if not username:
                raise AuthenticationFailed('Usuário ou senha inválidos.')

        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                raise AuthenticationFailed('Usuário ou senha inválidos.')
        except User.DoesNotExist:
            raise AuthenticationFailed('Usuário ou senha inválidos.')

        return user, None
