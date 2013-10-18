# -*- coding: utf-8 -*-
from django.contrib import messages
from django import http
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from libs.cobrebem.facade import Facade

from oscar.apps.checkout import views
from oscar.apps.payment.forms import BankcardForm
from oscar.apps.payment.models import SourceType, Source
from libs import crm


# Customise the core PaymentDetailsView to integrate Datacash
class PaymentDetailsView(views.PaymentDetailsView):

    def __init__(self, *args, **kwargs):
        self.cliente = crm.ClienteCRM()
        self.oportunidade = crm.OportunidadeCRM()
        self.produtos = []
        super(PaymentDetailsView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        # Add bankcard form to the template context
        ctx = super(PaymentDetailsView, self).get_context_data(**kwargs)
        ctx['bankcard_form'] = kwargs.get('bankcard_form', BankcardForm())
        return ctx

    def post(self, request, *args, **kwargs):
        if request.POST.get('action', '') == 'place_order':
            return self.do_place_order(request)

        # Check bankcard form is valid
        bankcard_form = BankcardForm(request.POST)
        if not bankcard_form.is_valid():
            # Bancard form invalid, re-render the payment details template
            self.preview = False
            ctx = self.get_context_data(**kwargs)
            ctx['bankcard_form'] = bankcard_form
            return self.render_to_response(ctx)

        # Render preview page (with completed bankcard form hidden).
        # Note, we don't write the bankcard details to the session or DB
        # as a security precaution.
        return self.render_preview(request, bankcard_form=bankcard_form)

    def do_place_order(self, request):
        # Double-check the bankcard data is still valid
        bankcard_form = BankcardForm(request.POST)
        if not bankcard_form.is_valid():
            messages.error(request, _("Invalid submission"))
            return http.HttpResponseRedirect(
                reverse('checkout:payment-details'))

        # Call oscar's submit method, passing through the bankcard object so it
        # gets passed to the 'handle_payment' method and can be used for the
        # submission to Datacash.
        bankcard = bankcard_form.bankcard
        return self.submit(request.basket,
                           payment_kwargs={'bankcard': bankcard})

    def handle_payment(self, order_number, total_incl_tax, **kwargs):
        bankcard = kwargs['bankcard']

        # Make request to DataCash - if there any problems (eg bankcard
        # not valid / request refused by bank) then an exception would be
        # raised and handled by the parent PaymentDetail view)
        ip = self.request.META['REMOTE_ADDR']
        facade = Facade()
        cobrebem_ref = facade.approval(self.oportunidade, order_number, total_incl_tax, bankcard, ip)

        self.oportunidade.data_pedido = now().strftime('%Y-%m-%d')
        self.oportunidade.valor_total = str(total_incl_tax)
        self.oportunidade.pag_credito_titular = 'Titular Teste'  # TODO: bankcard.cardholder
        self.oportunidade.pag_credito_vencimento = bankcard.expiry_month()
        self.oportunidade.pag_credito_bandeira = 'Bandeira Teste'  # TODO: bankcard.flag
        self.oportunidade.pag_credito_ultimos_digitos = bankcard.card_number[-4:]


        # Request was successful - record the "payment source".  As this
        # request was a 'pre-auth', we set the 'amount_allocated' - if we had
        # performed an 'auth' request, then we would set 'amount_debited'.
        source_type, _ = SourceType.objects.get_or_create(name='Cobrebem')
        source = Source(source_type=source_type,
                        currency='R$',
                        amount_allocated=total_incl_tax,
                        reference=cobrebem_ref)
        source.create_deferred_transaction("Approval", total_incl_tax, reference=cobrebem_ref, status=1)
        self.add_payment_source(source)
       
        # Also record payment event
        self.add_payment_event(
            'approval', total_incl_tax, reference=cobrebem_ref)

    def handle_successful_order(self, order):
        """
        Handle the various steps required after an order has been successfully
        placed.

        Override this view if you want to perform custom actions when an
        order is submitted.
        """
        # Send confirmation message (normally an email)

        profile = self.request.user.get_profile()

        self.cliente.cnpj = profile.cliente_cnpj
        self.cliente.razaosocial = profile.cliente_razaosocial
        self.cliente.logradouro = profile.cliente_logradouro
        self.cliente.numero = profile.cliente_numero
        self.cliente.complemento = profile.cliente_complemento
        self.cliente.bairro = profile.cliente_bairro
        self.cliente.cidade = profile.cliente_cidade
        self.cliente.estado = profile.cliente_uf
        self.cliente.pais = 'BR'
        self.cliente.cep = profile.cliente_cep
        self.cliente.sem_atividade = profile.cliente_situacao_cadastral.strip().lower() == 'ativa'

        for line in order.lines.all():
            produto = crm.ProdutoCRM()
            produto.codigo = line.partner_sku
            produto.quantidade = line.quantity
            produto.preco_venda = str(line.line_price_incl_tax)
            self.produtos.append(produto)

        client = crm.CRMClient()
        client.postar_compra(self.cliente, self.oportunidade, self.produtos)

        return None

        self.send_confirmation_message(order)

        # Flush all session data
        self.checkout_session.flush()

        # Save order id in session so thank-you page can load it
        self.request.session['checkout_order_id'] = order.id

        response = HttpResponseRedirect(self.get_success_url())
        self.send_signal(self.request, response, order)
        return response
