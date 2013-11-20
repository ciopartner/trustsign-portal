# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db.models import Model, CharField, ForeignKey, DateTimeField, TextField, DecimalField, EmailField, \
    OneToOneField, FileField, BooleanField, IntegerField, permalink, Manager, Q
from hashlib import md5
from django.utils import timezone
from oscar.core.loading import get_class

knu = None

User = get_user_model()
Order = get_class('order.models', 'Order')


class VoucherManager(Manager):
    use_for_related_fields = True

    def emitidos(self):
        return self.filter(Q(emissao__emission_status=Emissao.STATUS_EMITIDO) |
                           Q(emissao__emission_status=Emissao.STATUS_REEMITIDO))

    def revogados(self):
        return self.filter(emissao__emission_status=Emissao.STATUS_REVOGADO)


class Voucher(Model):
    # Certificados
    PRODUTO_SSL = 'ssl'
    PRODUTO_SSL_WILDCARD = 'ssl-wildcard'
    PRODUTO_SAN_UCC = 'ssl-san'
    PRODUTO_EV = 'ssl-ev'
    PRODUTO_EV_MDC = 'ssl-ev-mdc'
    PRODUTO_MDC = 'ssl-mdc'
    PRODUTO_JRE = 'ssl-jre'
    PRODUTO_CODE_SIGNING = 'ssl-cs'
    PRODUTO_SMIME = 'ssl-smime'

    # Domínios, FQDNs e Servidores Adicionais
    PRODUTO_SSL_MDC_DOMINIO = 'ssl-mdc-domain'
    PRODUTO_SSL_EV_MDC_DOMINIO = 'ssl-ev-mdc-domain'
    PRODUTO_SSL_SAN_FQDN = 'ssl-san-fqdn'
    PRODUTO_SSL_WILDCARD_SERVER = 'ssl-wildcard-servidor'

    # Assinaturas
    PRODUTO_PKI = 'pki'
    PRODUTO_SITE_SEGURO = 'site-seguro'
    PRODUTO_SITE_MONITORADO = 'site-monitorado'

    PRODUTO_CHOICES = (
        (PRODUTO_SSL, 'SSL'),
        (PRODUTO_SSL_WILDCARD, 'SSL Wildcard'),
        (PRODUTO_SAN_UCC, 'SAN UCC'),
        (PRODUTO_EV, 'EV'),
        (PRODUTO_EV_MDC, 'EV MDC'),
        (PRODUTO_MDC, 'MDC'),
        (PRODUTO_JRE, 'JRE'),
        (PRODUTO_CODE_SIGNING, 'Code Signing'),
        (PRODUTO_SMIME, 'S/MIME'),
        (PRODUTO_SSL_MDC_DOMINIO, 'MDC Domínio Adicional'),
        (PRODUTO_SSL_EV_MDC_DOMINIO, 'EV MDC Domínio Adicional'),
        (PRODUTO_SSL_SAN_FQDN, 'SAN FQDN Adicional'),
        (PRODUTO_SSL_WILDCARD_SERVER, 'Wildcard Servidor Adicional')
    )

    PRODUTO_CERTIFICADOS = [PRODUTO_SSL, PRODUTO_EV, PRODUTO_SSL_WILDCARD, PRODUTO_JRE, PRODUTO_CODE_SIGNING,
                            PRODUTO_SMIME, PRODUTO_SAN_UCC, PRODUTO_MDC, PRODUTO_EV_MDC]
    PRODUTO_ADICIONAIS   = [PRODUTO_SSL_SAN_FQDN, PRODUTO_SSL_MDC_DOMINIO, PRODUTO_SSL_EV_MDC_DOMINIO,
                            PRODUTO_SSL_WILDCARD_SERVER]
    PRODUTO_ASSINATURAS = [PRODUTO_PKI, PRODUTO_SITE_MONITORADO, PRODUTO_SITE_SEGURO]

    LINHA_DEGUSTACAO = 'trial'
    LINHA_BASIC = 'basic'
    LINHA_PRO = 'pro'
    LINHA_PRIME = 'prime'
    LINHA_CHOICES = (
        (LINHA_DEGUSTACAO, 'Trial'),
        (LINHA_BASIC, 'Basic'),
        (LINHA_PRO, 'Pro'),
        (LINHA_PRIME, 'Prime'),
    )

    VALIDADE_ANUAL = '1year'
    VALIDADE_BIANUAL = '2years'
    VALIDADE_TRIANUAL = '3years'
    VALIDADE_DEGUSTACAO = 'trial'
    VALIDADE_ASSINATURA_MENSAL = 'subscription_1m'
    VALIDADE_ASSINATURA_SEMESTRAL = 'subscription_6m'
    VALIDADE_ASSINATURA_ANUAL = 'subscription_12m'
    VALIDADE_CHOICES = (
        (VALIDADE_ANUAL, '1 ano'),
        (VALIDADE_BIANUAL, '2 anos'),
        (VALIDADE_TRIANUAL, '3 anos'),
        (VALIDADE_DEGUSTACAO, '30 dias'),
        (VALIDADE_ASSINATURA_MENSAL, 'Assinatura Mensal'),
        (VALIDADE_ASSINATURA_SEMESTRAL, 'Assinatura Semestral'),
        (VALIDADE_ASSINATURA_ANUAL, 'Assinatura Anual'),
    )

    ORDERCHANNEL_WEB = 'web'
    ORDERCHANNEL_INSIDE_SALES = 'inside-sales'
    ORDERCHANNEL_CHOICES = (
        (ORDERCHANNEL_WEB, 'Web'),
        (ORDERCHANNEL_INSIDE_SALES, 'Inside sales'),
    )

    crm_hash = CharField(max_length=128, unique=True)
    comodo_order = CharField(max_length=128, blank=True, null=True)
    order_number = CharField(max_length=32, blank=True, null=True)

    customer_cnpj = CharField(max_length=32)
    customer_companyname = CharField(max_length=128)
    customer_zip = CharField(max_length=16)
    customer_address1 = CharField(max_length=128)
    customer_address2 = CharField(max_length=8, blank=True, default='')
    customer_address3 = CharField(max_length=32, blank=True, default='')
    customer_address4 = CharField(max_length=64, blank=True, default='')
    customer_city = CharField(max_length=64)
    customer_state = CharField(max_length=2)
    customer_country = CharField(max_length=64)
    customer_registration_status = BooleanField(default=False)

    customer_callback_title = CharField(max_length=8, blank=True, default='')
    customer_callback_firstname = CharField(max_length=128, blank=True, default='')
    customer_callback_lastname = CharField(max_length=128, blank=True, default='')
    customer_callback_email = EmailField(blank=True, null=True)
    customer_callback_phone = CharField(max_length=16, blank=True, default='')
    customer_callback_note = CharField(max_length=128, blank=True, default='')

    ssl_code = CharField(max_length=128)
    ssl_url = CharField(max_length=200, blank=True, null=True)
    ssl_product = CharField(max_length=32, choices=PRODUTO_CHOICES)
    ssl_line = CharField(max_length=32, choices=LINHA_CHOICES)
    ssl_term = CharField(max_length=32, choices=VALIDADE_CHOICES)
    ssl_valid_from = DateTimeField(blank=True, null=True)
    ssl_valid_to = DateTimeField(blank=True, null=True)
    ssl_publickey = TextField(blank=True, null=True)
    ssl_revoked_date = DateTimeField(blank=True, null=True)
    ssl_domains_qty = IntegerField(blank=True, default=0)
    # TODO: apagar o campo abaixo
    ssl_seal_html = TextField(blank=True, default='')
    ssl_key_size = IntegerField(blank=True, null=True)
    ssl_username = CharField(max_length=32, blank=True, null=True)
    ssl_password = CharField(max_length=128, blank=True, null=True)

    order = ForeignKey(Order, related_name='vouchers', blank=True, null=True)
    # TODO: Criar o campo order_item e incluí-lo na ida e volta do CRM

    order_date = DateTimeField()
    order_item_value = DecimalField(decimal_places=2, max_digits=9)
    order_channel = CharField(max_length=64, choices=ORDERCHANNEL_CHOICES)
    order_canceled_date = DateTimeField(blank=True, null=True)
    order_canceled_reason = TextField(blank=True, null=True)

    objects = VoucherManager()

    def __unicode__(self):
        return '#%s (%s)' % (self.crm_hash, self.comodo_order)

    @property
    def tempo_em_espera(self):
        if self.ssl_product == self.PRODUTO_SSL:
            return 48
        if self.ssl_product == self.PRODUTO_EV:
            return 168
        if self.ssl_product == self.PRODUTO_SAN_UCC:
            return 72
        if self.ssl_product == self.PRODUTO_EV_MDC:
            return 240
        if self.ssl_product in (self.PRODUTO_SMIME, self.PRODUTO_CODE_SIGNING, self.PRODUTO_JRE):
            return 24

    @property
    def sla_estourado(self):
        return self.order_date + timedelta(hours=self.tempo_em_espera) < timezone.now()

    @property
    def sla_since(self):
        try:
            diff = timezone.now() - self.order_date
            return int(diff.total_seconds() / 3600)  # quantidade de horas passadas
        except Emissao.DoesNotExist:
            return 0

    def has_emissao_url(self):
        return self.ssl_product in(
            self.PRODUTO_SSL, self.PRODUTO_SSL_WILDCARD, self.PRODUTO_SAN_UCC, self.PRODUTO_MDC, self.PRODUTO_EV,
            self.PRODUTO_EV_MDC, self.PRODUTO_CODE_SIGNING, self.PRODUTO_JRE, self.PRODUTO_SMIME
        )

    @permalink
    def get_emissao_url(self):
        if self.ssl_product in (self.PRODUTO_SSL, self.PRODUTO_SSL_WILDCARD):
            view_name = 'form-emissao-nv1'
        elif self.ssl_product in (self.PRODUTO_SAN_UCC, self.PRODUTO_MDC):
            view_name = 'form-emissao-nv2'
        elif self.ssl_product == self.PRODUTO_EV:
            view_name = 'form-emissao-nv3'
        elif self.ssl_product == self.PRODUTO_EV_MDC:
            view_name = 'form-emissao-nv4'
        elif self.ssl_product in (self.PRODUTO_CODE_SIGNING, self.PRODUTO_JRE):
            view_name = 'form-emissao-nvA'
        elif self.ssl_product == self.PRODUTO_SMIME:
            view_name = 'form-emissao-nvB'
        else:
            return 'home'

        return view_name, (self.ssl_product, self.crm_hash)

    @permalink
    def get_revisao_url(self):
        if self.ssl_product in (self.PRODUTO_SSL, self.PRODUTO_SSL_WILDCARD):
            view_name = 'form-revisao-emissao-nv1'
        elif self.ssl_product in (self.PRODUTO_SAN_UCC, self.PRODUTO_MDC):
            view_name = 'form-revisao-emissao-nv2'
        elif self.ssl_product == self.PRODUTO_EV:
            view_name = 'form-revisao-emissao-nv3'
        elif self.ssl_product == self.PRODUTO_EV_MDC:
            view_name = 'form-revisao-emissao-nv4'
        elif self.ssl_product in (self.PRODUTO_CODE_SIGNING, self.PRODUTO_JRE):
            view_name = 'form-revisao-emissao-nvA'
        elif self.ssl_product == self.PRODUTO_SMIME:
            view_name = 'form-revisao-emissao-nvB'
        else:
            raise Exception('produto não possui url de emissao')

        return view_name, (self.ssl_product, self.crm_hash)

    @permalink
    def get_aprova_voucher_pendente_url(self):
        return 'aprova-voucher-pendente', (), {'crm_hash': self.crm_hash}

    @permalink
    def get_reemissao_url(self):
        return 'form-reemissao', (), {'crm_hash': self.crm_hash}

    @permalink
    def get_revogacao_url(self):
        return 'form-revogacao', (), {'crm_hash': self.crm_hash}

    @permalink
    def get_sealcode_url(self):
        return 'codigo-selo', (), {'crm_hash': self.crm_hash}

    @permalink
    def get_publickey_url(self):
        return 'chave-publica', (), {'crm_hash': self.crm_hash}

    @property
    def get_seal_html(self):
        try:
            emissao = self.emissao
        except Emissao.DoesNotExist:
            return ''

        seals_server_url = settings.SEALS_SERVER_URL
        url_validacao = '%s?url=%s' % (seals_server_url, emissao.emission_url)

        if self.ssl_line == Voucher.LINHA_BASIC:
            tipo = 'basic'
        elif self.ssl_line == Voucher.LINHA_PRO:
            tipo = 'pro'
        elif self.ssl_line == Voucher.LINHA_PRIME:
            tipo = 'prime'
        else:
            return ''

        hash_url = md5(emissao.emission_url).hexdigest()
        url_imagem_selo = '%s/static/selos-clientes/selo-%s-%s-pt.png' % (seals_server_url, tipo, hash_url)

        return '''<a href="%s" target="_blank">
<img name="trustseal" alt="Site Autêntico" src="%s/static/" border="0" title="Clique para Validar" />
</a>''' % (url_validacao, url_imagem_selo)

    @property
    def is_complemento_certificado(self):
        """
        Retorna verdadeiro se for um FQDN, Domínio ou Servidor Adicional, checando contra as categorias do produto
        """
        # TODO: Quando o order_item estiver indo e voltando do CRM, alterar a consulta para o
        # voucher.emissao.order_item.product.categories in ....
        return self.ssl_product in self.PRODUTO_ADICIONAIS

    @property
    def is_complemento_utilizado(self):
        """
        Retorna True se for um domínio, fqdn ou servidor adicional e já tiver sido utilizado.
        """
        return self.is_complemento_certificado and hasattr(self, 'emissao') and \
               self.emissao.emission_status != self.STATUS_NAO_EMITIDO

    @property
    def is_complemento_disponivel(self):
        """
        Retorna True se for um domínio, fqdn ou servidor adicional e não tiver sido utilizado.
        """
        return self.is_complemento_certificado and not hasattr(self, 'emissao')

    @property
    def is_status_available(self):
        """
        Retorna True se o status é de voucher disponível para emissão
        """
        return not hasattr(self, 'emissao')

    @property
    def is_status_ongoing(self):
        """
        Retorna True se o status é de emissão em andamento
        """
        STATUS_ONGOING = [Emissao.STATUS_EMISSAO_APROVACAO_PENDENTE, Emissao.STATUS_EMISSAO_ENVIO_COMODO_PENDENTE,
                          Emissao.STATUS_EMISSAO_ENVIADO_COMODO, Emissao.STATUS_REEMISSAO_ENVIADO_COMODO,
                          Emissao.STATUS_REEMISSAO_ENVIO_COMODO_PENDENTE,
                          Emissao.STATUS_REVOGACAO_APROVACAO_PENDENTE, Emissao.STATUS_REVOGACAO_ENVIADO_COMODO,
                          Emissao.STATUS_REVOGACAO_ENVIO_COMODO_PENDENTE,
                          ]
        return hasattr(self, 'emissao') and self.emissao.emission_status in STATUS_ONGOING

    @property
    def is_status_done(self):
        """
        Retorna True se o status é de emissão terminada
        """
        STATUS_DONE = [Emissao.STATUS_EMITIDO, Emissao.STATUS_EMITIDO_SELO_PENDENTE, Emissao.STATUS_REEMITIDO,
                       Emissao.STATUS_REVOGADO, Emissao.STATUS_REVOGADO_SELO_PENDENTE,
                       Emissao.STATUS_ADICIONAL_USADO]
        return hasattr(self, 'emissao') and self.emissao.emission_status in STATUS_DONE


class DominioValidator(RegexValidator):
    regex = r'^(\*\.)?[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*(\.[A-Za-z]{2,})$'
    message = 'Domínio inválido'


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

    STATUS_NAO_EMITIDO = 0

    STATUS_EMISSAO_APROVACAO_PENDENTE = 1
    STATUS_EMISSAO_ENVIO_COMODO_PENDENTE = 2
    STATUS_EMISSAO_ENVIADO_COMODO = 3
    STATUS_EMITIDO_SELO_PENDENTE = 4
    STATUS_EMITIDO = 5

    STATUS_REEMISSAO_ENVIO_COMODO_PENDENTE = 10
    STATUS_REEMISSAO_ENVIADO_COMODO = 11
    STATUS_REEMITIDO = 12

    STATUS_REVOGACAO_APROVACAO_PENDENTE = 20
    STATUS_REVOGACAO_ENVIO_COMODO_PENDENTE = 21
    STATUS_REVOGACAO_ENVIADO_COMODO = 22
    STATUS_REVOGADO_SELO_PENDENTE = 23
    STATUS_REVOGADO = 24

    STATUS_EXPIRADO = 90

    STATUS_OCORREU_ERRO_COMODO = 91

    STATUS_ADICIONAL_USADO = 12

    STATUS_CHOICES = (
        (STATUS_NAO_EMITIDO, 'Não Emitido'),

        (STATUS_EMISSAO_APROVACAO_PENDENTE, 'Emissão Pendente de Revisão'),
        (STATUS_EMISSAO_ENVIO_COMODO_PENDENTE, 'Emissão Em Processamento'),
        (STATUS_EMISSAO_ENVIADO_COMODO, 'Emissão Solicitada'),
        (STATUS_EMITIDO_SELO_PENDENTE, 'Certificado Emitido, Selo Pendente'),
        (STATUS_EMITIDO, 'Certificado Emitido'),

        (STATUS_REEMISSAO_ENVIO_COMODO_PENDENTE, 'Reemissão Em Processamento'),
        (STATUS_REEMISSAO_ENVIADO_COMODO, 'Reemissão Solicitada'),
        (STATUS_REEMITIDO, 'Certificado Reemitido'),

        (STATUS_REVOGACAO_APROVACAO_PENDENTE, 'Revogação Pendente de Revisão'),
        (STATUS_REVOGACAO_ENVIO_COMODO_PENDENTE, 'Revogação Em Processamento'),
        (STATUS_REVOGACAO_ENVIADO_COMODO, 'Revogação Solicitada'),
        (STATUS_REVOGADO_SELO_PENDENTE, 'Certificado Revogado, Selo Pendente'),
        (STATUS_REVOGADO, 'Certificado Revogado'),

        (STATUS_EXPIRADO, 'Certificado Expirado'),
        (STATUS_OCORREU_ERRO_COMODO, 'Ocorreu um erro interno'),

        (STATUS_ADICIONAL_USADO, 'Adicional usado'),
    )

    voucher = OneToOneField(Voucher, related_name='emissao')
    crm_hash = CharField(max_length=128, unique=True)
    comodo_order = CharField(max_length=128, blank=True, null=True)

    requestor_user = ForeignKey(User, related_name='emissoes')
    requestor_timestamp = DateTimeField(auto_now_add=True)

    emission_url = CharField(max_length=256, blank=True, null=True, validators=[DominioValidator()])
    emission_urls = TextField(blank=True, null=True)
    emission_csr = TextField(blank=True, null=True)

    emission_dcv_emails = TextField(blank=True, null=True)
    emission_publickey_sendto = EmailField(blank=True, null=True)
    emission_server_type = IntegerField(choices=SERVIDOR_TIPO_CHOICES, blank=True, null=True)

    emission_reviewer = ForeignKey(User, related_name='emissoes_revisadas', null=True, blank=True)
    emission_approver = ForeignKey(User, related_name='emissoes_aprovadas', null=True, blank=True)

    emission_primary_dn = CharField(max_length=256, null=True, blank=True)

    emission_assignment_letter = FileField(upload_to='uploads/cartas/', blank=True, null=True)
    emission_articles_of_incorporation = FileField(upload_to='uploads/contratos_sociais/', blank=True, null=True)
    emission_address_proof = FileField(upload_to='uploads/comprovantes_endereco/', blank=True, null=True)
    emission_ccsa = FileField(upload_to='uploads/ccsas/', blank=True, null=True)  # comodo cert. subscriber agreement
    emission_evcr = FileField(upload_to='uploads/evcrs/', blank=True, null=True)  # ev certificate request
    emission_phone_proof = FileField(upload_to='uploads/conta-telefone/', blank=True, null=True)
    emission_id = FileField(upload_to='uploads/docs/', blank=True, null=True)

    emission_cost = DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)

    emission_revoke_password = CharField(max_length=128, blank=True, null=True)

    emission_status = IntegerField(choices=STATUS_CHOICES, default=STATUS_NAO_EMITIDO)
    emission_error_message = CharField(max_length=256, blank=True, null=True)

    emission_certificate = TextField(blank=True, null=True)
    emission_mail_attachment_path = CharField(blank=True, null=True, max_length=256)

    class Meta:
        verbose_name = 'emissão'
        verbose_name_plural = 'emissões'
        permissions = (
            ("do_emission_process", "Can do emission precess"),
            ("view_pending_emission", "Can view pending emission"),
        )

    def __unicode__(self):
        return '#%s (%s)' % (self.crm_hash, self.comodo_order)

    def get_dominios_x_emails(self):
        return zip(self.get_lista_dominios(), self.get_lista_emails())

    def get_lista_emails(self):
        return self.emission_dcv_emails.split(' ')

    def get_lista_dominios(self):
        return self.emission_urls.split(' ')

    def get_lista_dominios_linha(self):
        return '\n'.join(self.get_lista_dominios())

    @property
    def em_processamento(self):
        return self.emission_status in (
            Emissao.STATUS_EMISSAO_APROVACAO_PENDENTE,
            Emissao.STATUS_EMISSAO_ENVIO_COMODO_PENDENTE,
            Emissao.STATUS_EMISSAO_ENVIADO_COMODO,
            Emissao.STATUS_EMITIDO_SELO_PENDENTE,

            Emissao.STATUS_REEMISSAO_ENVIO_COMODO_PENDENTE,
            Emissao.STATUS_REEMISSAO_ENVIADO_COMODO,

            Emissao.STATUS_REVOGACAO_APROVACAO_PENDENTE,
            Emissao.STATUS_REVOGACAO_ENVIO_COMODO_PENDENTE,
            Emissao.STATUS_REVOGACAO_ENVIADO_COMODO,
            Emissao.STATUS_REVOGADO_SELO_PENDENTE,
        )

    @property
    def expirado(self):
        return self.emission_status == Emissao.STATUS_EXPIRADO

    @property
    def emitido(self):
        return self.emission_status in (Emissao.STATUS_EMITIDO, Emissao.STATUS_REEMITIDO)

    def aprova(self, user):
        if self.emission_status == Emissao.STATUS_EMISSAO_APROVACAO_PENDENTE:
            self.emission_status = Emissao.STATUS_EMISSAO_ENVIO_COMODO_PENDENTE
        elif self.emission_status == Emissao.STATUS_REVOGACAO_APROVACAO_PENDENTE:
            self.emission_status = Emissao.STATUS_REVOGACAO_ENVIO_COMODO_PENDENTE

        self.emission_approver = user


class Revogacao(Model):
    crm_hash = CharField(max_length=128, unique=True)
    emission = ForeignKey(Emissao, related_name='revogacoes')
    revoke_reason = TextField()

    class Meta:
        verbose_name = 'revogação'
        verbose_name_plural = 'revogações'

    def __unicode__(self):
        return '#%s' % self.crm_hash


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
            instance.cliente_pais = 'BR'
        else:
            raise Exception('Ocorreu um erro ao consultar seu CNPJ: %s' % r.desc_erro)