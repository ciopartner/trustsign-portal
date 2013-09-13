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
            ('cliente_cnpj', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('cliente_razaosocial', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('cliente_cep', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('cliente_logradouro', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('cliente_numero', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('cliente_complemento', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('cliente_bairro', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('cliente_cidade', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('cliente_uf', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('cliente_pais', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('cliente_situacao_cadastral', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('cliente_callback_tratamento', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('cliente_callback_nome', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('cliente_callback_sobrenome', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('cliente_callback_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('cliente_callback_telefone', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('cliente_callback_username', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('cliente_callback_observacao', self.gf('django.db.models.fields.CharField')(default=u'', max_length=128, blank=True)),
            ('ssl_url', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('ssl_produto', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('ssl_linha', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('ssl_validade', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('ssl_valido_de', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('ssl_valido_ate', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('ssl_publickey', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('ssl_revogado_data', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('ssl_dominios_qtde', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('pedido_data', self.gf('django.db.models.fields.DateTimeField')()),
            ('pedido_item_valor', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=2)),
            ('pedido_canal', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('pedido_cancelado_data', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('selo_html', self.gf('django.db.models.fields.TextField')()),
            ('criacao_historico', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'certificados', ['Voucher'])

        # Adding model 'Emissao'
        db.create_table(u'certificados_emissao', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('voucher', self.gf('django.db.models.fields.related.OneToOneField')(related_name=u'emissao', unique=True, to=orm['certificados.Voucher'])),
            ('crm_hash', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('comodo_order', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('solicitante_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'emissoes', to=orm['auth.User'])),
            ('solicitante_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('emissao_url', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('emissao_validacao_email', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('emissao_certificado_envio_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('emissao_servidor_tipo', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('emissao_csr', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('emissao_aprovador', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('emissao_fqdns', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('emissao_primary_dn', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('emissao_carta', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('emissao_contrato_social', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('emissao_comprovante_endereco', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('emissao_ccsa', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('emissao_evcr', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('emissao_conta_telefone', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('emissao_doc_identificacao', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('emissao_custo', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=9, decimal_places=2, blank=True)),
            ('emissao_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
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
            'comodo_order': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'crm_hash': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'emissao_aprovador': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'emissao_carta': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'emissao_ccsa': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'emissao_certificado_envio_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'emissao_comprovante_endereco': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'emissao_conta_telefone': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'emissao_contrato_social': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'emissao_csr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'emissao_custo': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '9', 'decimal_places': '2', 'blank': 'True'}),
            'emissao_doc_identificacao': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'emissao_evcr': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'emissao_fqdns': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'emissao_primary_dn': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'emissao_servidor_tipo': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'emissao_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'emissao_url': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'emissao_validacao_email': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'solicitante_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'solicitante_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'emissoes'", 'to': u"orm['auth.User']"}),
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
            'cliente_bairro': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'cliente_callback_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'cliente_callback_nome': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'cliente_callback_observacao': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '128', 'blank': 'True'}),
            'cliente_callback_sobrenome': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'cliente_callback_telefone': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'cliente_callback_tratamento': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'cliente_callback_username': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'cliente_cep': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'cliente_cidade': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'cliente_cnpj': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'cliente_complemento': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'cliente_logradouro': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'cliente_numero': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'cliente_pais': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'cliente_razaosocial': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'cliente_situacao_cadastral': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'cliente_uf': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'comodo_order': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'criacao_historico': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'crm_hash': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pedido_canal': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'pedido_cancelado_data': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'pedido_data': ('django.db.models.fields.DateTimeField', [], {}),
            'pedido_item_valor': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'selo_html': ('django.db.models.fields.TextField', [], {}),
            'ssl_dominios_qtde': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ssl_linha': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'ssl_produto': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'ssl_publickey': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ssl_revogado_data': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'ssl_url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'ssl_validade': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'ssl_valido_ate': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'ssl_valido_de': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
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