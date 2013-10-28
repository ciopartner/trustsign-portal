# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DominioInvalidoEmail'
        db.create_table(u'website_dominioinvalidoemail', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'website', ['DominioInvalidoEmail'])


    def backwards(self, orm):
        # Deleting model 'DominioInvalidoEmail'
        db.delete_table(u'website_dominioinvalidoemail')


    models = {
        u'website.dominioinvalidoemail': {
            'Meta': {'object_name': 'DominioInvalidoEmail'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['website']