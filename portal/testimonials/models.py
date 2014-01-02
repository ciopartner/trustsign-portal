# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from mezzanine.core.models import Orderable
from django.db import models


class Testimonial(Orderable):
    name = models.CharField(max_length=100, verbose_name='Nome')
    designation = models.CharField(max_length=100, verbose_name='Título/Cargo', null=True, blank=True)
    testimonial = models.TextField(verbose_name='Testemunho')
    time = models.IntegerField(verbose_name='Tempo de exibição', help_text='Em segundos')
