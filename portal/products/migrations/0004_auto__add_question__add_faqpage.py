# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Question'
        db.create_table(u'products_question', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.TextField')()),
            ('answer', self.gf('django.db.models.fields.TextField')()),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(related_name='questions', to=orm['products.FAQPage'])),
        ))
        db.send_create_signal(u'products', ['Question'])

        # Adding model 'FAQPage'
        db.create_table(u'products_faqpage', (
            (u'page_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pages.Page'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'products', ['FAQPage'])


    def backwards(self, orm):
        # Deleting model 'Question'
        db.delete_table(u'products_question')

        # Deleting model 'FAQPage'
        db.delete_table(u'products_faqpage')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'generic.assignedkeyword': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'AssignedKeyword'},
            '_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignments'", 'to': u"orm['generic.Keyword']"}),
            'object_pk': ('django.db.models.fields.IntegerField', [], {})
        },
        u'generic.keyword': {
            'Meta': {'object_name': 'Keyword'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'pages.page': {
            'Meta': {'ordering': "('titles',)", 'object_name': 'Page'},
            '_meta_title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            '_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'content_model': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'expiry_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'gen_description': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_menus': ('mezzanine.pages.fields.MenusField', [], {'default': '(1, 2, 3)', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'in_sitemap': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'keywords': ('mezzanine.generic.fields.KeywordsField', [], {'object_id_field': "'object_pk'", 'to': u"orm['generic.AssignedKeyword']", 'frozen_by_south': 'True'}),
            'keywords_string': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'login_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['pages.Page']"}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'short_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'titles': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'})
        },
        u'products.faqpage': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'FAQPage', '_ormbases': [u'pages.Page']},
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'products.product': {
            'Meta': {'ordering': "['-order']", 'object_name': 'Product', '_ormbases': [u'pages.Page']},
            'cart_add_url': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '999'}),
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'tab_title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'youtube_title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'youtube_url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'products.products': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'Products', '_ormbases': [u'pages.Page']},
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'products.question': {
            'Meta': {'object_name': 'Question'},
            'answer': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'questions'", 'to': u"orm['products.FAQPage']"}),
            'question': ('django.db.models.fields.TextField', [], {})
        },
        u'products.tabcontent': {
            'Meta': {'object_name': 'TabContent'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tabs'", 'to': u"orm['products.Product']"}),
            'tab_description': ('django.db.models.fields.TextField', [], {}),
            'tab_description_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'tab_short_description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'tab_title': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['products']