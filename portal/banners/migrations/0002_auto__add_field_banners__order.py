# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Banners._order'
        db.add_column(u'banners_banners', '_order',
                      self.gf('django.db.models.fields.IntegerField')(null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Banners._order'
        db.delete_column(u'banners_banners', '_order')


    models = {
        u'banners.banners': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'Banners'},
            '_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'expire_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['banners']