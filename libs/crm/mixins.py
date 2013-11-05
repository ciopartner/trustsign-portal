# coding=utf-8
from __future__ import unicode_literals
from django.utils.timezone import now
from oscar.core.loading import get_class
import crm
from ecommerce.website.utils import formata_cnpj

Bankcard = get_class('payment.models', 'Bankcard')


class OscarToCRMMixin(object):
    def send_order_to_crm(self, order):
        """
        Send the order to CRM
        """
        cliente = self.get_cliente_crm(order)
        contato = self.get_contato_crm(order)
        oportunidade = self.get_oportunidade_crm(order)
        produtos = self.get_produtos_crm(order)

        crm_client = crm.CRMClient()
        crm_client.postar_compra(cliente, contato, oportunidade, produtos)

    @staticmethod
    def get_cliente_crm(order):
        """
        Return a ClientCRM to send to CRM
        """
        profile = order.user.get_profile()
        cliente = crm.ClienteCRM()

        if not profile.cliente_cnpj:
            raise crm.CRMClient.CRMError('Cliente sem CNPJ cadastrado')

        cliente.cnpj = formata_cnpj(profile.cliente_cnpj) if len(profile.cliente_cnpj) < 18 else profile.cliente_cnpj
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

        cliente.tipo_negocio = profile.cliente_tipo_negocio
        cliente.is_ecommerce = profile.cliente_ecommerce
        cliente.fonte_do_potencial = profile.cliente_fonte_potencial

        return cliente

    @staticmethod
    def get_contato_crm(order):
        """
        Return a Contact to send to CRM
        """
        profile = order.user.get_profile()
        contato = crm.ContatoCRM()

        contato.nome = profile.callback_nome
        contato.sobrenome = profile.callback_sobrenome
        contato.email = profile.callback_email_corporativo
        contato.telefone = profile.callback_telefone_principal

        return contato

    @staticmethod
    def get_oportunidade_crm(order):
        """
        Return a oportunity to send to CRM
        """
        source = order.sources.all()[0]

        try:
            bankcard = source.bankcard
        except Bankcard.DoesNotExists:
            raise crm.CRMClient.CRMError('Falta os dados do cartão de crédito')

        transaction_id = source.reference

        oportunidade = crm.OportunidadeCRM()
        oportunidade.numero_pedido = 100000 + order.pk
        oportunidade.pag_credito_transacao_id = transaction_id
        oportunidade.data_pedido = now().strftime('%Y-%m-%d')
        oportunidade.valor_total = str(order.total_incl_tax)

        #TODO: colocar if quando implementar os outros meios de pagamento
        if bankcard:
            oportunidade.tipo_pagamento = oportunidade.TIPO_CARTAO_CREDITO
            oportunidade.pag_credito_titular = bankcard.name
            oportunidade.pag_credito_vencimento = bankcard.expiry_month()
            oportunidade.pag_credito_bandeira = bankcard.card_type
            oportunidade.pag_credito_ultimos_digitos = bankcard.number[-4:]

        return oportunidade

    @staticmethod
    def get_produtos_crm(order):
        """
        Return a list of products to send to CRM
        """
        produtos = []

        for line in order.lines.all():
            produto = crm.ProdutoCRM()
            produto.codigo = line.partner_sku
            produto.quantidade = line.quantity
            produto.preco_unitario = str(line.unit_price_incl_tax)
            produto.preco_total = str(line.line_price_excl_tax)
            produtos.append(produto)

        return produtos