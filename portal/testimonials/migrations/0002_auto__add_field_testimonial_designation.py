# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Testimonial.designation'
        db.add_column(u'testimonials_testimonial', 'designation',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Testimonial.designation'
        db.delete_column(u'testimonials_testimonial', 'designation')


    models = {
        u'testimonials.testimonial': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'Testimonial'},
            '_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'designation': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'testimonial': ('django.db.models.fields.TextField', [], {}),
            'time': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['testimonials']