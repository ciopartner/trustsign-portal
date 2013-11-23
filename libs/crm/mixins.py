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

        # Passo 1: Fazer login
        crm_client = crm.CRMClient()
        crm_client.login()

        # Passo 2: Criar ou atualizar o cliente
        cliente_id = crm_client.update_or_create_account(cliente)

        # Passo 3: Criar ou recuperar o contato
        contato.account_id = cliente_id
        contato_id = crm_client.get_or_create_contact(contato)

        # Passo 4: Criar uma oportunidade para cada transaction_id
        # Isso se faz necessário porque temos a seguinte regra de pagamento via cartão de crédito:
        # - a soma de todos os certificados geram uma transaction;
        # - a soma de todas as assinaturas gera uma nova transaction;

        # Para cada transação, criar uma oportunidade
        sources = order.sources.all()
        transactions = []
        for s in sources:
            for t in s.transactions.all():
                transactions.append(t)

        # Produtos com preço zerado não possuem transaction, porém precisam ser enviados para o CRM
        if order.lines.filter(paymentevent__reference__isnull=True).exists():
            transactions.append(None)

        # Para cada transação, crie uma oportunidade e inclua todos os produtos daquela transação
        for t in transactions:
            # Cria a oportunidade
            oportunidade = self.get_oportunidade_crm(order, transaction=t)
            oportunidade.account_id = cliente_id
            oportunidade.contact_id = contato_id
            oportunidade_id = crm_client.set_entry_opportunities(oportunidade)

            # Cria os produtos da oportunidade
            produtos = self.get_produtos_crm(order, transaction=t)
            for produto in produtos:
                produto.account_id = contato_id
                produto.opportunity_id = oportunidade_id
                crm_client.set_entry_products(produto)

        crm_client.logout()

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
        cliente.nomefantasia = profile.cliente_nomefantasia
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
    def get_oportunidade_crm(order, transaction):
        """
        Return a oportunity to send to CRM
        A intenção é criar uma oportunidade para cada transação de cartão de crédito.
        """
        transaction_id = transaction.reference if transaction else 'n/a'
        oportunidade = crm.OportunidadeCRM()
        oportunidade.numero_pedido = order.number
        oportunidade.data_pedido = now().strftime('%Y-%m-%d')
        oportunidade.data_pagto = now().strftime('%Y-%m-%d')
        oportunidade.valor_total = str(order.total_incl_tax)
        oportunidade.parcelas = '1'

        if transaction is None:
            # Para o caso de pedido de valor zerado (trial)
            oportunidade.tipo_pagamento = oportunidade.TIPO_GRATIS
        elif transaction.boleto_id:
            # Para pagamento com boleto
            oportunidade.tipo_pagamento = oportunidade.TIPO_BOLETO
            oportunidade.pag_boleto_transacao_id = transaction_id
        elif transaction.debitcard_id:
            # Para pagamento com cartão de débito
            oportunidade.tipo_pagamento = oportunidade.TIPO_CARTAO_DEBITO
            oportunidade.pag_debito_transacao_id = transaction_id
        elif transaction.bankcard_id:
            # Para pagamento com cartão de crédito
            oportunidade.tipo_pagamento = oportunidade.TIPO_CARTAO_CREDITO
            oportunidade.pag_credito_titular = transaction.bankcard.name
            oportunidade.pag_credito_vencimento = transaction.bankcard.expiry_month()
            oportunidade.pag_credito_bandeira = transaction.bankcard.card_type
            oportunidade.pag_credito_ultimos_digitos = transaction.bankcard.number[-4:]
            oportunidade.pag_credito_transacao_id = transaction_id
            oportunidade.parcelas = transaction.bankcard.qtd_parcelas
        else:
            # Para pagamento fiado....
            raise crm.CRMClient.CRMError('Faltam os dados de pagamento')

        return oportunidade

    @staticmethod
    def get_produtos_crm(order, transaction):
        """
        Return a list of products to send to CRM
        Note that products without transaction (as trial) are also processed
        """
        transaction_id = transaction.reference if transaction else None
        produtos = []

        lines = order.lines.filter(paymentevent__reference=transaction_id) if transaction else \
                order.lines.filter(paymentevent_reference__isnull=True)
        for line in lines:
            produto = crm.ProdutoCRM()
            produto.codigo = line.partner_sku
            produto.quantidade = line.quantity
            produto.preco_unitario = str(line.unit_price_incl_tax)
            produto.preco_total = str(line.line_price_excl_tax)
            produtos.append(produto)

        return produtos