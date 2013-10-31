# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Voucher.legacy_imported'
        db.delete_column(u'certificados_voucher', 'legacy_imported')

        # Changing field 'Voucher.customer_callback_email'
        db.alter_column(u'certificados_voucher', 'customer_callback_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True))

        # Changing field 'Voucher.customer_registration_status'
        db.alter_column(u'certificados_voucher', 'customer_registration_status', self.gf('django.db.models.fields.BooleanField')())

    def backwards(self, orm):
        # Adding field 'Voucher.legacy_imported'
        db.add_column(u'certificados_voucher', 'legacy_imported',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # Changing field 'Voucher.customer_callback_email'
        db.alter_column(u'certificados_voucher', 'customer_callback_email', self.gf('django.db.models.fields.EmailField')(default='editar@editar.com', max_length=75))

        # Changing field 'Voucher.customer_registration_status'
        db.alter_column(u'certificados_voucher', 'customer_registration_status', self.gf('django.db.models.fields.CharField')(max_length=128))

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
            'customer_address2': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '8', 'blank': 'True'}),
            'customer_address3': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '32', 'blank': 'True'}),
            'customer_address4': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '64', 'blank': 'True'}),
            'customer_callback_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'customer_callback_firstname': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '128', 'blank': 'True'}),
            'customer_callback_lastname': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '128', 'blank': 'True'}),
            'customer_callback_note': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '128', 'blank': 'True'}),
            'customer_callback_password': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'customer_callback_phone': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '16', 'blank': 'True'}),
            'customer_callback_title': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '8', 'blank': 'True'}),
            'customer_callback_username': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'customer_city': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'customer_cnpj': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'customer_companyname': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'customer_country': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'customer_registration_status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'customer_state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'customer_zip': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'ssl_seal_html': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
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