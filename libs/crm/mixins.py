# coding=utf-8
from django.utils.timezone import now
from oscar.core.loading import get_class
import crm
Bankcard = get_class('payment.models', 'Bankcard')


class OscarToCRMMixin(object):
    def send_order_to_crm(self, order):
        cliente = self.get_cliente_crm(order.user)
        oportunidade = self.get_oportunidade_crm(order)
        produtos = self.get_produtos_crm(order)

        client = crm.CRMClient()
        client.postar_compra(cliente, oportunidade, produtos)

    @staticmethod
    def get_cliente_crm(user):
        """
        Return a ClientCRM to send to CRM
        """
        profile = user.get_profile()
        cliente = crm.ClienteCRM()

        cliente.cnpj = profile.cliente_cnpj
        cliente.razaosocial = profile.cliente_razaosocial
        cliente.logradouro = profile.cliente_logradouro
        cliente.numero = profile.cliente_numero
        cliente.complemento = profile.cliente_complemento
        cliente.bairro = profile.cliente_bairro
        cliente.cidade = profile.cliente_cidade
        cliente.estado = profile.cliente_uf
        cliente.pais = 'BR'
        cliente.cep = profile.cliente_cep
        cliente.sem_atividade = profile.cliente_situacao_cadastral.strip().lower() == 'ativa'

        return cliente

    @staticmethod
    def get_oportunidade_crm(order):
        source = order.sources.all()[0]
        try:
            bankcard = source.bankcard
        except Bankcard.DoesNotExists:
            raise crm.CRMClient.CRMError('Falta os dados do cartão de crédito')
        transaction_id = source.reference
        oportunidade = crm.OportunidadeCRM()
        oportunidade.pag_credito_transacao_id = transaction_id
        oportunidade.data_pedido = now().strftime('%Y-%m-%d')
        oportunidade.valor_total = str(source.amount_allocated)
        oportunidade.pag_credito_titular = bankcard.name
        oportunidade.pag_credito_vencimento = bankcard.expiry_month()
        oportunidade.pag_credito_bandeira = bankcard.card_type
        oportunidade.pag_credito_ultimos_digitos = bankcard.number[-4:]

        return oportunidade

    @staticmethod
    def get_produtos_crm(order):
        produtos = []

        for line in order.lines.all():
            produto = crm.ProdutoCRM()
            produto.codigo = line.partner_sku
            produto.quantidade = line.quantity
            produto.preco_venda = str(line.line_price_incl_tax)
            produtos.append(produto)

        return produtos