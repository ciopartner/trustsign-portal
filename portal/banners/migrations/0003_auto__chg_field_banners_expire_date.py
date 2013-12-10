# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Banners.expire_date'
        db.alter_column(u'banners_banners', 'expire_date', self.gf('django.db.models.fields.DateTimeField')(null=True))

    def backwards(self, orm):

        # Changing field 'Banners.expire_date'
        db.alter_column(u'banners_banners', 'expire_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 12, 9, 0, 0)))

    models = {
        u'banners.banners': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'Banners'},
            '_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'expire_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['banners']