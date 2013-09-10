# coding=utf-8
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.db.models import Model, CharField, ForeignKey, DateTimeField, TextField, DecimalField, EmailField, \
    OneToOneField, FileField, BooleanField, IntegerField
from django.db.models.signals import pre_save
import knu

User = get_user_model()


class Voucher(Model):
    #TODO: verificar a relação dos códigos e definir codigo produto s+s e sm
    PRODUTO_SITE_SEGURO = 99999
    PRODUTO_SITE_MONITORADO = 88888
    PRODUTO_SSL = 488
    PRODUTO_SSL_WILDCARD = 489
    PRODUTO_SAN_UCC = 492
    PRODUTO_EV = 337
    PRODUTO_EV_MDC = 410
    PRODUTO_TRIAL = 43
    PRODUTO_MDC = 335
    PRODUTO_CHOICES = (
        (PRODUTO_SITE_SEGURO, 'Site + Seguro'),
        (PRODUTO_SITE_MONITORADO, 'Site Monitorado'),
        (PRODUTO_SSL, 'SSL'),
        (PRODUTO_SSL_WILDCARD, 'SSL Wildcard'),
        (PRODUTO_SAN_UCC, 'SAN UCC'),
        (PRODUTO_EV, 'EV'),
        (PRODUTO_EV_MDC, 'EV MDC'),
        (PRODUTO_TRIAL, 'Trial'),
        (PRODUTO_MDC, 'MDC')
    )

    LINHA_BASIC = 1
    LINHA_PRO = 2
    LINHA_PRIME = 3
    LINHA_CHOICES = (
        (LINHA_BASIC, 'Basic'),
        (LINHA_PRO, 'Pro'),
        (LINHA_PRIME, 'Prime'),
    )

    PERIODO_ANUAL = 1
    PERIODO_BIANUAL = 2
    PERIODO_TRIANUAL = 3
    PERIODO_CHOICES = (
        (PERIODO_ANUAL, 'Anual'),
        (PERIODO_BIANUAL, 'Bianual'),
        (PERIODO_TRIANUAL, 'Trianual'),
    )

    crm_hash = CharField(max_length=128)
    comodo_order = CharField(max_length=128, blank=True, null=True)

    cliente_cnpj = CharField(max_length=32)
    cliente_razaosocial = CharField(max_length=128)
    cliente_cep = CharField(max_length=16)
    cliente_logradouro = CharField(max_length=128)
    cliente_numero = CharField(max_length=8)
    cliente_complemento = CharField(max_length=32)
    cliente_bairro = CharField(max_length=64)
    cliente_cidade = CharField(max_length=64)
    cliente_uf = CharField(max_length=2)
    cliente_pais = CharField(max_length=64)

    cliente_situacao_cadastral = CharField(max_length=128)
    cliente_callback_nome = CharField(max_length=128)
    cliente_callback_email = EmailField()
    cliente_callback_telefone = CharField(max_length=16)
    contato_observacao = CharField(max_length=128)

    ssl_url = CharField(max_length=200, blank=True, null=True)
    ssl_produto = IntegerField(choices=PRODUTO_CHOICES)
    ssl_linha = IntegerField(choices=LINHA_CHOICES)
    ssl_periodo = IntegerField(choices=PERIODO_CHOICES)
    ssl_valido_de = DateTimeField(blank=True, null=True)
    ssl_valido_ate = DateTimeField(blank=True, null=True)
    ssl_publickey = TextField(blank=True, null=True)
    ssl_certificado_tipo = CharField(max_length=32, blank=True, null=True)
    ssl_certificado_linha = CharField(max_length=32, blank=True, null=True)
    ssl_certificado_validade = CharField(max_length=32, blank=True, null=True)
    ssl_revogado_data = DateTimeField(blank=True, null=True)
    ssl_dominios_qtde = IntegerField(blank=True, null=True)

    pedido_data = DateTimeField()
    pedido_item_valor = DecimalField(decimal_places=2, max_digits=9)
    pedido_canal = CharField(max_length=64)
    pedido_cancelado_data = DateTimeField(blank=True, null=True)

    selo_html = TextField()
    criacao_historico = BooleanField(default=False)


# class Pedido(Model):  # TODO: Substituir por abstract do oscar
#     knu_html = TextField()
#     crm_envio_data = DateTimeField()
#     pedido_cancelado_data = DateTimeField(blank=True, null=True)
#
#     cliente_cnpj = CharField(max_length=32)
#     cliente_razaosocial = CharField(max_length=128)
#     cliente_cep = CharField(max_length=16)
#     cliente_logradouro = CharField(max_length=128)
#     cliente_numero = CharField(max_length=8)
#     cliente_complemento = CharField(max_length=32)
#     cliente_bairro = CharField(max_length=64)
#     cliente_cidade = CharField(max_length=64)
#     cliente_uf = CharField(max_length=2)
#     cliente_pais = CharField(max_length=64)
#
#     cliente_situacao_cadastral = CharField(max_length=128)
#     cliente_callback_nome = CharField(max_length=128)
#     cliente_callback_email = EmailField()
#     cliente_callback_telefone = CharField(max_length=16)
#     contato_observacao = CharField(max_length=128)


class Emissao(Model):
    SERVIDOR_TIPO_CHOICES = (
        (1, 'AOL'),
        (2, 'Apache/ModSSL'),
        (3, 'Apache-SSL (Ben-SSP, not Strongold)'),
        (4, 'C2Net Stronghold'),
        (33, 'Cisco 3000 Series VPN Concentrator'),
        (34, 'Citrix'),
        (5, 'Cobalt Raq'),
        (6, 'Covalent Server Software'),
        (29, 'Ensim'),
        (32, 'H-Sphere'),
        (7, 'IBM HTTP Server'),
        (8, 'IBM Internet Connection Server'),
        (9, 'iPlanet'),
        (10, 'Java Web Server (Javasoft / Sun'),
        (11, 'Lotus Domino'),
        (12, 'Lotus Domino Go!'),
        (13, 'Microsoft IIS 1.x to 4.x'),
        (14, 'Microsoft IIS 5.x to 6.x'),
        (35, 'Microsoft IIS 7.x and later'),
        (15, 'Netscape Enterprise Server'),
        (16, 'Netscape FastTrack'),
        (36, 'Nginx'),
        (17, 'Novell Web Server'),
        (18, 'Oracle'),
        (30, 'Plesk'),
        (19, 'Quid Pro Quo'),
        (20, 'R3 SSL Server'),
        (21, 'Raven SSL'),
        (22, 'RedHat Linux'),
        (23, 'SAP Web Application Server'),
        (24, 'Tomcat'),
        (25, 'Website Professional'),
        (26, 'Webstar 4.x and later'),
        (27, 'Webten (from Tenon)'),
        (31, 'WHM/cPanel'),
        (28, 'Zeus Web Server'),
        (-1, 'Other'),
    )

    STATUS_CHOICES = (
        (1, 'Finalizada'),
        (2, 'Aguardando aprovação manual'),
    )
    voucher = OneToOneField(Voucher, primary_key=True)
    crm_hash = CharField(max_length=128)
    comodo_order = CharField(max_length=128)

    solicitante_user = ForeignKey(User, related_name='emissoes')
    solicitante_canal = CharField(max_length=64)
    solicitante_timestamp = DateTimeField(auto_now_add=True)

    emissao_url = CharField(max_length=256, blank=True, null=True)
    emissao_validacao_email = CharField(max_length=128, blank=True, null=True)
    emissao_certificado_envio_email = EmailField(blank=True, null=True)
    emissao_servidor_tipo = IntegerField(choices=SERVIDOR_TIPO_CHOICES, blank=True, null=True)

    emissao_csr = TextField(blank=True, null=True)

    emissao_aprovador = CharField(max_length=128, null=True, blank=True)

    emissao_fqdns = TextField(blank=True, null=True)
    emissao_primary_dn = CharField(max_length=256, null=True, blank=True)

    emissao_carta = FileField(upload_to='uploads/cartas/', blank=True, null=True)
    emissao_contrato_social = FileField(upload_to='uploads/contratos_sociais/', blank=True, null=True)
    emissao_comprovante_endereco = FileField(upload_to='uploads/comprovantes_endereco/', blank=True, null=True)
    emissao_ccsa = FileField(upload_to='uploads/ccsas/', blank=True, null=True)  # comodo cert. subscriber agreement
    emissao_evcr = FileField(upload_to='uploads/evcrs/', blank=True, null=True)  # ev certificate request

    emissao_status = IntegerField(choices=STATUS_CHOICES)


class Revogacao(Model):
    crm_hash = CharField(max_length=128)
    emissao = ForeignKey(Emissao, related_name='revogacoes')
    revogacao_motivo = TextField()


def pedido_consulta_knu(sender, instance, **kwargs):
    if not instance.pk and instance.cliente_cnpj:  # pk = None significa que vai inserir o voucher
        r = knu.receitaCNPJ(instance.cliente_cnpj)
        if r.erro == 0:
            instance.cliente_razaosocial = r.nome_empresarial
            instance.cliente_cep = r.cep
            instance.cliente_logradouro = r.logradouro
            instance.cliente_numero = r.numero
            instance.cliente_complemento = r.complemento
            instance.cliente_bairro = r.bairro
            instance.cliente_cidade = r.municipio
            instance.cliente_uf = r.uf
            instance.cliente_pais = 'Brasil'
        else:
            raise Exception('Ocorreu um erro ao consultar seu CNPJ: %s' % r.desc_erro)

# pre_save.connect(pedido_consulta_knu, sender=Pedido)