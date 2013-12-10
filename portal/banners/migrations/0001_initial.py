# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Banners'
        db.create_table(u'banners_banners', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('expire_date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'banners', ['Banners'])


    def backwards(self, orm):
        # Deleting model 'Banners'
        db.delete_table(u'banners_banners')


    models = {
        u'banners.banners': {
            'Meta': {'object_name': 'Banners'},
            'expire_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['banners']