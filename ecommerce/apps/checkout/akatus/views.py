# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from oscar.core.loading import get_class
import requests
from ecommerce.apps.payment.forms import DebitcardForm
from ecommerce.website.utils import remove_message
from libs.akatus import facade as akatus

from oscar.apps.payment.exceptions import UnableToTakePayment, InvalidGatewayRequestError
from oscar.apps.checkout import views
from libs.crm.mixins import OscarToCRMMixin
import logging

BankcardForm = get_class('payment.forms', 'BankcardForm')
SourceType = get_class('payment.models', 'SourceType')
Source = get_class('payment.models', 'Source')
Transaction = get_class('payment.models', 'Transaction')
Boleto = get_class('payment.models', 'Boleto')

log = logging.getLogger('ecommerce.checkout.views')


class PaymentDetailsView(views.PaymentDetailsView, OscarToCRMMixin):
    """
    For taking the details of payment and creating the order

    The class is deliberately split into fine-grained methods, responsible for
    only one thing.  This is to make it easier to subclass and override just
    one component of functionality.

    All projects will need to subclass and customise this class.
    """

    preview = False

    def get(self, request, *args, **kwargs):
        error_response = self.get_error_response()
        if error_response:
            return error_response
        return super(PaymentDetailsView, self).get(request, *args, **kwargs)

    def get_error_response(self):
        if self.request.method == 'POST':
            if not self.valida_contrato_ssl() or not self.valida_contrato_sitemonitorado() or \
                    not self.valida_contrato_siteseguro() or not self.valida_contrato_pki():
                messages.error(self.request, 'Você precisa aceitar os termos de uso dos produtos selecionados')
                return HttpResponseRedirect(reverse('checkout:payment-details'))
        return super(PaymentDetailsView, self).get_error_response()

    def valida_contrato_ssl(self):
        return not self.request.basket.tem_contrato_ssl() or self.request.POST.get('aceita_contrato_ssl', '') == '1'

    def valida_contrato_siteseguro(self):
        return not self.request.basket.tem_contrato_siteseguro() or self.request.POST.get('aceita_contrato_ss', '') == '1'

    def valida_contrato_sitemonitorado(self):
        return not self.request.basket.tem_contrato_sitemonitorado() or self.request.POST.get('aceita_contrato_sm', '') == '1'

    def valida_contrato_pki(self):
        return not self.request.basket.tem_contrato_pki() or self.request.POST.get('aceita_contrato_pki', '') == '1'

    def get_context_data(self, **kwargs):
        # Add here anything useful to be rendered in templates
        ctx = super(PaymentDetailsView, self).get_context_data(**kwargs)
        ctx['bankcard_form'] = kwargs.get('bankcard_form', BankcardForm())
        ctx['debitcard_form'] = kwargs.get('debitcard_form', DebitcardForm())

        return ctx

    def post(self, request, *args, **kwargs):
        """
        This method is designed to be overridden by subclasses which will
        validate the forms from the payment details page.  If the forms are
        valid then the method can call submit()
        """
        error_response = self.get_error_response()
        if error_response:
            return error_response

        source_type = request.POST.get('source-type')

        if source_type == 'no-payment':
            submission = self.build_submission()
            if submission['order_total'].incl_tax > 0:
                raise UnableToTakePayment('Forma de pagamento inválida')
            return self.submit(**submission)

        if source_type == 'akatus-creditcard':
            bankcard_form = BankcardForm(request.POST)
            if not bankcard_form.is_valid():
                # Bankcard form invalid, re-render the payment details template
                self.preview = False
                ctx = self.get_context_data(**kwargs)
                ctx['bankcard_form'] = bankcard_form
                return self.render_to_response(ctx)
            submission = self.build_submission()
            submission['payment_kwargs']['bankcard'] = bankcard_form.bankcard
            return self.submit(**submission)

        if source_type == 'akatus-debitcard':
            debitcard_form = DebitcardForm(request.POST)
            if not debitcard_form.is_valid():
                # Debitcard form invalid, re-render the payment details template
                self.preview = False
                ctx = self.get_context_data(**kwargs)
                ctx['debitcard_form'] = debitcard_form
                return self.render_to_response(ctx)
            submission = self.build_submission()
            submission['payment_kwargs']['debitcard'] = debitcard_form.debitcard
            return self.submit(**submission)

        if source_type == 'akatus-boleto':
            submission = self.build_submission()
            submission['payment_kwargs']['boleto'] = Boleto()
            return self.submit(**submission)

        raise UnableToTakePayment('Forma de pagamento inválida')

    def handle_payment(self, order_number, total_incl_tax, **kwargs):
        """
        This method is responsible for taking the payment.
        """
        payment_source = self.request.POST.get('source-type')

        if payment_source == 'akatus-boleto':
            return self.handle_payment_boleto(order_number, total_incl_tax, **kwargs)

        elif payment_source == 'akatus-creditcard':
            return self.handle_payment_credito(order_number, total_incl_tax, **kwargs)

        elif payment_source == 'akatus-debitcard':
            return self.handle_payment_debito(order_number, total_incl_tax, **kwargs)
        elif payment_source == 'no-payment':
            return

        raise UnableToTakePayment

    def handle_payment_credito(self, order_number, total_incl_tax, **kwargs):
        """
        This method is responsible for taking the payment of credit card
        """
        bankcard = kwargs['bankcard']

        # Make request to DataCash - if there any problems (eg bankcard
        # not valid / request refused by bank) then an exception would be
        # raised and handled by the parent PaymentDetail view)
        facade = akatus.Facade()
        try:
            response = facade.post_payment(self.request, order_number, bankcard=bankcard, tipo='akatus-creditcard')
            transaction_id = response['transacao']
        except InvalidGatewayRequestError as e:
            raise UnableToTakePayment(e.message)

        bankcard.user = self.request.user
        bankcard.save()

        # Request was successful - record the "payment source".  As this
        # request was a 'pre-auth', we set the 'amount_allocated' - if we had
        # performed an 'auth' request, then we would set 'amount_debited'.
        source_type, _ = SourceType.objects.get_or_create(name='akatus-creditcard')
        source = Source(source_type=source_type,
                        currency='BRL',
                        amount_debited=total_incl_tax.incl_tax,
                        reference=transaction_id)
        # When we create a transaction, we have to set a txn_type that should be debit or refund
        source.create_deferred_transaction("akatus-creditcard-init", total_incl_tax.incl_tax, reference=transaction_id, status=1, bankcard=bankcard)
        self.add_payment_source(source)

        # Also record payment event
        # When we create the payment event, we have to set a txn_type that should be debit or refund
        self.add_payment_event('akatus-creditcard-init', total_incl_tax.incl_tax, reference=transaction_id)

    def handle_payment_debito(self, order_number, total_incl_tax, **kwargs):
        """
        This method is responsible for taking the payment of debit card
        """
        debitcard = kwargs['debitcard']

        # Make request to DataCash - if there any problems (eg bankcard
        # not valid / request refused by bank) then an exception would be
        # raised and handled by the parent PaymentDetail view)
        facade = akatus.Facade()

        response = facade.post_payment(self.request, order_number, debitcard=debitcard, tipo='akatus-debitcard')
        transaction_id = response['transacao']
        url_redirect = response['url_retorno']

        debitcard.user = self.request.user
        debitcard.debitcard_url = url_redirect
        debitcard.save()

        # Request was successful - record the "payment source".  As this
        # request was a 'pre-auth', we set the 'amount_allocated' - if we had
        # performed an 'auth' request, then we would set 'amount_debited'.
        source_type, _ = SourceType.objects.get_or_create(name='akatus-debitcard')
        source = Source(source_type=source_type,
                        currency='BRL',
                        amount_allocated=total_incl_tax.incl_tax,
                        reference=transaction_id)

        source.create_deferred_transaction("akatus-debitcard-init", total_incl_tax.incl_tax, reference=transaction_id, status=1, debitcard=debitcard)
        self.add_payment_source(source)

        # Also record payment event
        self.add_payment_event('akatus-debitcard-init', total_incl_tax.incl_tax, reference=transaction_id)

    def handle_payment_boleto(self, order_number, total_incl_tax, **kwargs):
        """
        This method is responsible for taking the payment of boleto
        """
        boleto = kwargs['boleto']

        facade = akatus.Facade()
        response = facade.post_payment(self.request, order_number, tipo='akatus-boleto')
        transaction_id = response['transacao']
        url_redirect = response['url_retorno']

        boleto.user = self.request.user
        boleto.boleto_url = url_redirect
        try:
            boleto.boleto_html = requests.get(url_redirect).text
        except Exception:
            pass
        boleto.save()

        # Request was successful - record the "payment source".  As this
        # request was a 'pre-auth', we set the 'amount_allocated' - if we had
        # performed an 'auth' request, then we would set 'amount_debited'.
        source_type, _ = SourceType.objects.get_or_create(name='akatus-boleto')
        source = Source(source_type=source_type,
                        currency='BRL',
                        amount_allocated=total_incl_tax.incl_tax,
                        reference=transaction_id)

        source.create_deferred_transaction("akatus-boleto-init", total_incl_tax.incl_tax, reference=transaction_id, status=1, boleto=boleto)
        self.add_payment_source(source)

        # Also record payment event
        self.add_payment_event('akatus-boleto-init', total_incl_tax.incl_tax, reference=transaction_id)

    def handle_order_placement(self, order_number, user, basket, shipping_address, shipping_method, total, **kwargs):
        """
        Write out the order models and return the appropriate HTTP response

        We deliberately pass the basket in here as the one tied to the request
        isn't necessarily the correct one to use in placing the order.  This
        can happen when a basket gets frozen.
        """
        order = self.place_order(order_number, user, basket, shipping_address, shipping_method, total, **kwargs)
        basket.submit()

        if self.request.POST.get('source-type') == 'no-payment':
            order.set_status('Pago')

        return self.handle_successful_order(order)


class ShippingAddressView(views.ShippingAddressView):

    def get(self, request, *args, **kwargs):

        r = super(ShippingAddressView, self).get(request, *args, **kwargs)
        remove_message(request, u'Sua cesta não requer um endereço para ser submetida')
        return r


class ThankYouView(views.ThankYouView):
    def get_context_data(self, **kwargs):
        context = super(ThankYouView, self).get_context_data(**kwargs)
        order = context['order']
        transacoes_com_url = []

        transactions = Transaction.objects.select_related(
            'boleto',
            'debitcard',
        ).filter(
            txn_type__in=('akatus-boleto-init', 'akatus-debitcard-init'),
            source__order=order,
        )

        for transaction in transactions:
            if transaction.source.source_type.name == 'akatus-boleto':
                transacoes_com_url.append(('boleto', transaction.boleto.boleto_url))
            else:
                transacoes_com_url.append(('debitcard', transaction.debitcard.debitcard_url))

        context.update({
            'transacoes_com_url': transacoes_com_url  # uma lista de  (<tipo>, <url>) onde <tipo> = boleto ou debitcard
        })

        return context


class StatusChangedView(TemplateView):
    template_name = 'checkout/akatus/status_changed.html'

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        r = super(StatusChangedView, self).render_to_response(context, **response_kwargs)
        log.info('AKATUS STATUS CHANGED GET: {}'.format(self.request.GET))
        log.info('AKATUS STATUS CHANGED POST: {}'.format(self.request.POST))
        return r