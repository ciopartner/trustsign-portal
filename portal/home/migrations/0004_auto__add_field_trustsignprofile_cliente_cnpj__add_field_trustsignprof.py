# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TrustSignProfile.cliente_cnpj'
        db.add_column(u'home_trustsignprofile', 'cliente_cnpj',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True),
                      keep_default=False)

        # Adding field 'TrustSignProfile.cliente_razaosocial'
        db.add_column(u'home_trustsignprofile', 'cliente_razaosocial',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True),
                      keep_default=False)

        # Adding field 'TrustSignProfile.cliente_logradouro'
        db.add_column(u'home_trustsignprofile', 'cliente_logradouro',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True),
                      keep_default=False)

        # Adding field 'TrustSignProfile.cliente_numero'
        db.add_column(u'home_trustsignprofile', 'cliente_numero',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=16, blank=True),
                      keep_default=False)

        # Adding field 'TrustSignProfile.cliente_complemento'
        db.add_column(u'home_trustsignprofile', 'cliente_complemento',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=64, blank=True),
                      keep_default=False)

        # Adding field 'TrustSignProfile.cliente_cep'
        db.add_column(u'home_trustsignprofile', 'cliente_cep',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=8, blank=True),
                      keep_default=False)

        # Adding field 'TrustSignProfile.cliente_bairro'
        db.add_column(u'home_trustsignprofile', 'cliente_bairro',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True),
                      keep_default=False)

        # Adding field 'TrustSignProfile.cliente_cidade'
        db.add_column(u'home_trustsignprofile', 'cliente_cidade',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True),
                      keep_default=False)

        # Adding field 'TrustSignProfile.cliente_uf'
        db.add_column(u'home_trustsignprofile', 'cliente_uf',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True),
                      keep_default=False)

        # Adding field 'TrustSignProfile.cliente_situacao_cadastral'
        db.add_column(u'home_trustsignprofile', 'cliente_situacao_cadastral',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True),
                      keep_default=False)

        # Adding field 'TrustSignProfile.callback_nome'
        db.add_column(u'home_trustsignprofile', 'callback_nome',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True),
                      keep_default=False)

        # Adding field 'TrustSignProfile.callback_sobrenome'
        db.add_column(u'home_trustsignprofile', 'callback_sobrenome',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True),
                      keep_default=False)

        # Adding field 'TrustSignProfile.callback_email_corporativo'
        db.add_column(u'home_trustsignprofile', 'callback_email_corporativo',
                      self.gf('django.db.models.fields.EmailField')(default='', max_length=75, blank=True),
                      keep_default=False)

        # Adding field 'TrustSignProfile.callback_telefone_principal'
        db.add_column(u'home_trustsignprofile', 'callback_telefone_principal',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=16, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'TrustSignProfile.cliente_cnpj'
        db.delete_column(u'home_trustsignprofile', 'cliente_cnpj')

        # Deleting field 'TrustSignProfile.cliente_razaosocial'
        db.delete_column(u'home_trustsignprofile', 'cliente_razaosocial')

        # Deleting field 'TrustSignProfile.cliente_logradouro'
        db.delete_column(u'home_trustsignprofile', 'cliente_logradouro')

        # Deleting field 'TrustSignProfile.cliente_numero'
        db.delete_column(u'home_trustsignprofile', 'cliente_numero')

        # Deleting field 'TrustSignProfile.cliente_complemento'
        db.delete_column(u'home_trustsignprofile', 'cliente_complemento')

        # Deleting field 'TrustSignProfile.cliente_cep'
        db.delete_column(u'home_trustsignprofile', 'cliente_cep')

        # Deleting field 'TrustSignProfile.cliente_bairro'
        db.delete_column(u'home_trustsignprofile', 'cliente_bairro')

        # Deleting field 'TrustSignProfile.cliente_cidade'
        db.delete_column(u'home_trustsignprofile', 'cliente_cidade')

        # Deleting field 'TrustSignProfile.cliente_uf'
        db.delete_column(u'home_trustsignprofile', 'cliente_uf')

        # Deleting field 'TrustSignProfile.cliente_situacao_cadastral'
        db.delete_column(u'home_trustsignprofile', 'cliente_situacao_cadastral')

        # Deleting field 'TrustSignProfile.callback_nome'
        db.delete_column(u'home_trustsignprofile', 'callback_nome')

        # Deleting field 'TrustSignProfile.callback_sobrenome'
        db.delete_column(u'home_trustsignprofile', 'callback_sobrenome')

        # Deleting field 'TrustSignProfile.callback_email_corporativo'
        db.delete_column(u'home_trustsignprofile', 'callback_email_corporativo')

        # Deleting field 'TrustSignProfile.callback_telefone_principal'
        db.delete_column(u'home_trustsignprofile', 'callback_telefone_principal')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'home.trustsignprofile': {
            'Meta': {'object_name': 'TrustSignProfile'},
            'bio': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'callback_email_corporativo': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '75', 'blank': 'True'}),
            'callback_nome': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'callback_sobrenome': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'callback_telefone_principal': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16', 'blank': 'True'}),
            'cliente_bairro': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'cliente_cep': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '8', 'blank': 'True'}),
            'cliente_cidade': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'cliente_cnpj': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32', 'blank': 'True'}),
            'cliente_complemento': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'cliente_logradouro': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'cliente_numero': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16', 'blank': 'True'}),
            'cliente_razaosocial': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'cliente_situacao_cadastral': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'cliente_uf': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'perfil': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'tagline': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['home']