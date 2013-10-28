# coding=utf-8
from __future__ import unicode_literals
from django.db.models import CharField, Model


class DominioInvalidoEmail(Model):
    nome = CharField(max_length=128)

    class Meta:
        verbose_name = 'domínio inválido para e-mail'
        verbose_name_plural = 'domínios inválidos para e-mail'
        ordering = ('nome', )

    def __unicode__(self):
        return self.nome