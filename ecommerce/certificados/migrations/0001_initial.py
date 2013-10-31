# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Voucher'
        db.create_table(u'certificados_voucher', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('crm_hash', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('comodo_order', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('order_number', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('legacy_imported', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('customer_cnpj', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('customer_companyname', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('customer_zip', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('customer_address1', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('customer_address2', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('customer_address3', self.gf('django.db.models.fields.CharField')(default=u'', max_length=32, blank=True)),
            ('customer_address4', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('customer_city', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('customer_state', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('customer_country', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('customer_registration_status', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('customer_callback_title', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('customer_callback_firstname', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('customer_callback_lastname', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('customer_callback_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('customer_callback_phone', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('customer_callback_username', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('customer_callback_password', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('customer_callback_note', self.gf('django.db.models.fields.CharField')(default=u'', max_length=128, blank=True)),
            ('ssl_url', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('ssl_product', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('ssl_line', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('ssl_term', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('ssl_valid_from', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('ssl_valid_to', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('ssl_publickey', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('ssl_revoked_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('ssl_domains_qty', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('ssl_seal_html', self.gf('django.db.models.fields.TextField')()),
            ('order_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('order_item_value', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=2)),
            ('order_channel', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('order_canceled_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'certificados', ['Voucher'])

        # Adding model 'Emissao'
        db.create_table(u'certificados_emissao', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('voucher', self.gf('django.db.models.fields.related.OneToOneField')(related_name=u'emissao', unique=True, to=orm['certificados.Voucher'])),
            ('crm_hash', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('comodo_order', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('requestor_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'emissoes', to=orm['auth.User'])),
            ('requestor_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('emission_url', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('emission_dcv_emails', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('emission_publickey_sendto', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('emission_server_type', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('emission_csr', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('emission_approver', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'emissoes_aprovadas', null=True, to=orm['auth.User'])),
            ('emission_fqdns', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('emission_primary_dn', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('emission_assignment_letter', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('emission_articles_of_incorporation', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('emission_address_proof', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('emission_ccsa', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('emission_evcr', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('emission_phone_proof', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('emission_id', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('emission_cost', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=9, decimal_places=2, blank=True)),
            ('emission_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'certificados', ['Emissao'])

        # Adding model 'Revogacao'
        db.create_table(u'certificados_revogacao', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('crm_hash', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('emissao', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'revogacoes', to=orm['certificados.Emissao'])),
            ('revogacao_motivo', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'certificados', ['Revogacao'])


    def backwards(self, orm):
        # Deleting model 'Voucher'
        db.delete_table(u'certificados_voucher')

        # Deleting model 'Emissao'
        db.delete_table(u'certificados_emissao')

        # Deleting model 'Revogacao'
        db.delete_table(u'certificados_revogacao')


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
        u'certificados.emissao': {
            'Meta': {'object_name': 'Emissao'},
            'comodo_order': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'crm_hash': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'emission_address_proof': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'emission_approver': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'emissoes_aprovadas'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'emission_articles_of_incorporation': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'emission_assignment_letter': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'emission_ccsa': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'emission_cost': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '9', 'decimal_places': '2', 'blank': 'True'}),
            'emission_csr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'emission_dcv_emails': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'emission_evcr': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'emission_fqdns': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'emission_id': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'emission_phone_proof': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'emission_primary_dn': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'emission_publickey_sendto': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'emission_server_type': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'emission_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'emission_url': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'requestor_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'requestor_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'emissoes'", 'to': u"orm['auth.User']"}),
            'voucher': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'emissao'", 'unique': 'True', 'to': u"orm['certificados.Voucher']"})
        },
        u'certificados.revogacao': {
            'Meta': {'object_name': 'Revogacao'},
            'crm_hash': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'emissao': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'revogacoes'", 'to': u"orm['certificados.Emissao']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'revogacao_motivo': ('django.db.models.fields.TextField', [], {})
        },
        u'certificados.voucher': {
            'Meta': {'object_name': 'Voucher'},
            'comodo_order': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'crm_hash': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'customer_address1': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'customer_address2': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'customer_address3': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '32', 'blank': 'True'}),
            'customer_address4': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'customer_callback_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'customer_callback_firstname': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'customer_callback_lastname': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'customer_callback_note': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '128', 'blank': 'True'}),
            'customer_callback_password': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'customer_callback_phone': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'customer_callback_title': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'customer_callback_username': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'customer_city': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'customer_cnpj': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'customer_companyname': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'customer_country': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'customer_registration_status': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'customer_state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'customer_zip': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'legacy_imported': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'order_canceled_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'order_channel': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'order_date': ('django.db.models.fields.DateTimeField', [], {}),
            'order_item_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'order_number': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'ssl_domains_qty': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'ssl_line': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'ssl_product': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'ssl_publickey': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ssl_revoked_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'ssl_seal_html': ('django.db.models.fields.TextField', [], {}),
            'ssl_term': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'ssl_url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'ssl_valid_from': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'ssl_valid_to': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['certificados']