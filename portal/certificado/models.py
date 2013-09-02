from django.contrib.auth import get_user_model
from django.db.models import Model, CharField, ForeignKey, DateTimeField, TextField, DecimalField, EmailField, \
    OneToOneField, FileField, BooleanField, IntegerField

User = get_user_model()


class Voucher(Model):
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

    #TODO: verificar com alessandro a necessidade dos campos abaixo (nao ta no trello..)
    selo_html = TextField()
    criacao_historico = BooleanField(default=False)


Pedido = object()  # TODO: substituir FK Emissao > Pedido


class Emissao(Model):
    voucher = OneToOneField(Voucher, primary_key=True)

    comodo_order = CharField(max_length=128)

    solicitante_user = ForeignKey(User, related_name='emissoes')
    solicitante_canal = CharField(max_length=64)
    solicitante_timestamp = DateTimeField(auto_now_add=True)

    emissao_pedido = ForeignKey(Pedido, related_name='emissoes')
    emissao_url = CharField(max_length=256)
    emissao_carta = FileField(blank=True, null=True)
    emissao_validacao_email = CharField(max_length=128, blank=True, null=True)
    emissao_certificado_envio_email = EmailField(blank=True, null=True)
    emissao_servidor_tipo = CharField(max_length=128, blank=True, null=True)

    emissao_csr = TextField(blank=True, null=True)

    emissao_aprovador = CharField(max_length=128, null=True, blank=True)

    emissao_fqdns = TextField(blank=True, null=True)

    emissao_contrato_social = FileField(blank=True, null=True)
    emissao_comprovante_endereco = FileField(blank=True, null=True)
    emissao_ccsa = FileField(blank=True, null=True)
    emissao_evcr = FileField(blank=True, null=True)