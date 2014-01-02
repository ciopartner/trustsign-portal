# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Testimonial'
        db.create_table(u'testimonials_testimonial', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('_order', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('testimonial', self.gf('django.db.models.fields.TextField')()),
            ('time', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'testimonials', ['Testimonial'])


    def backwards(self, orm):
        # Deleting model 'Testimonial'
        db.delete_table(u'testimonials_testimonial')


    models = {
        u'testimonials.testimonial': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'Testimonial'},
            '_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'testimonial': ('django.db.models.fields.TextField', [], {}),
            'time': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['testimonials']