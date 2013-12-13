# -*- coding: utf-8 -*-
import datetime
from django.db import models
from django.db.models import Q
from django.db.models.manager import Manager
from django.utils import timezone
from mezzanine.core.models import Orderable

Orderable._meta.get_field('_order').verbose_name = 'Ordem'


class BannersManager(Manager):
    def get_in_date(self):
        return self.filter(
            Q(expire_date__lte=datetime.date.today()) | Q(expire_date__isnull=True),
            pub_date__lte=timezone.now()
        )


class Banners(Orderable):
    image = models.ImageField(upload_to='banners')
    url = models.URLField(blank=True, null=True)
    pub_date = models.DateTimeField(verbose_name=u'Data de publicação')
    expire_date = models.DateTimeField(verbose_name=u'Data de expiração', null=True, blank=True)
    objects = BannersManager()

    def __unicode__(self):
            return "Banner" + str(self._order)