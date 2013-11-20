# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from copy import copy
from decimal import Decimal
from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.core.mail import send_mail
from django.http import Http404
from django.views.generic import TemplateView
from oscar.core.loading import get_class
from ecommerce.apps.payment.forms import DebitcardForm
from ecommerce.website.utils import remove_message, send_template_email
from libs.akatus import facade as akatus

from oscar.apps.payment.exceptions import UnableToTakePayment, InvalidGatewayRequestError
from oscar.apps.checkout import views
from libs.crm.mixins import OscarToCRMMixin
from time import sleep
import requests
import logging

BankcardForm = get_class('payment.forms', 'BankcardForm')
SourceType = get_class('payment.models', 'SourceType')
Source = get_class('payment.models', 'Source')
Transaction = get_class('payment.models', 'Transaction')
Boleto = get_class('payment.models', 'Boleto')
Order = get_class('order.models', 'Order')
Line = get_class('order.models', 'Line')

PaymentEventType = get_class('order.models', 'PaymentEventType')
PaymentEvent = get_class('order.models', 'PaymentEvent')
PaymentEventQuantity = get_class('order.models', 'PaymentEventQuantity')


log = logging.getLogger('ecommerce.checkout.views')


class PaymentEventMixin(object):
    def add_payment_event(self, event_type_name, amount, reference='', lines=None):
        """
        Record a payment event for creation once the order is placed
        """
        event_type, __ = PaymentEventType.objects.get_or_create(
            name=event_type_name)
        # We keep a local cache of payment events
        if self._payment_events is None:
            self._payment_events = []
        event = PaymentEvent(
            event_type=event_type, amount=amount,
            reference=reference)
        self._payment_events.append((event, lines))

    def save_payment_events(self, order):
        """
        Saves any relevant payment events for this order
        """
        if not self._payment_events:
            return

        for event, lines in self._payment_events:
            event.order = order
            event.save()

            order_lines = order.lines.all()

            if lines is None:
                lines = order_lines

            for line in lines:
                for order_line in order_lines:
                    if order_line.product_id == line.product_id:
                        PaymentEventQuantity.objects.create(event=event, line=order_line, quantity=order_line.quantity)
                        break


class PaymentDetailsView(PaymentEventMixin, views.PaymentDetailsView, OscarToCRMMixin):
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

        basket = self.request.basket

        total_compra = basket.total_incl_tax

        total_assinaturas = sum(line.line_price_incl_tax
                                for line in basket.get_lines_assinaturas())

        total_certificados = total_compra - total_assinaturas

        if total_certificados <= 0:
            parcelas_certificados = []
        else:
            facade = akatus.Facade()

            try:
                response = facade.get_payment_installments(total_certificados)
            except InvalidGatewayRequestError as e:
                raise UnableToTakePayment(e.message)

            juros = Decimal(response['descricao'].split('%')[0].replace(',', '.'))

            parcelas_certificados = [
                {
                    'qtd': p['quantidade'],
                    'valor_total': p['total'],
                    'valor_parcela': p['valor'],
                    'juros': juros
                } for p in response['parcelas']]

            parcelas_certificados[0]['juros'] = Decimal(0)

        ctx.update({
            'bankcard_form': kwargs.get('bankcard_form', BankcardForm()),
            'debitcard_form': kwargs.get('debitcard_form', DebitcardForm()),

            'total_compra': total_compra,
            'total_assinaturas': total_assinaturas,
            'total_certificados': total_certificados,

            'parcelas': {
                'assinaturas': total_assinaturas,
                'certificados': parcelas_certificados
            }
        })

        if self.request.method == 'POST':
            source_type = self.request.POST.get('source-type')
            if source_type == 'akatus-creditcard':
                ctx['bankcard_form'] = kwargs.get('bankcard_form', BankcardForm(data=self.request.POST))
            elif source_type == 'akatus-debitcard':
                ctx['debitcard_form'] = kwargs.get('bankcard_form', DebitcardForm(data=self.request.POST))

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

        if not self.valida_contrato_ssl() or not self.valida_contrato_sitemonitorado() or \
                not self.valida_contrato_siteseguro() or not self.valida_contrato_pki():
            raise UnableToTakePayment('Você precisa aceitar os termos de uso dos produtos selecionados')

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

        lines_assinaturas = self.request.basket.get_lines_assinaturas()
        lines_certificados = self.request.basket.get_lines_certificados()

        source_type, _ = SourceType.objects.get_or_create(name='akatus-creditcard')

        parcelas = self.request.POST.get('certificado_parcela')

        bankcard.qtd_parcelas = parcelas

        bankcard_com_numero = copy(bankcard)

        bankcard.user = self.request.user
        bankcard.save()

        if not parcelas:
            raise UnableToTakePayment('Selecione a quantidade de parcelas no pagamento por cartão de crédito')

        for lines in (lines_assinaturas, lines_certificados):
            if lines:
                try:
                    response = facade.post_payment(self.request, order_number, lines=lines,
                                                   bankcard=bankcard_com_numero, tipo='akatus-creditcard',
                                                   parcelas=parcelas)
                    transaction_id = response['transacao']
                except InvalidGatewayRequestError as e:
                    raise UnableToTakePayment(e.message)

                total = sum(line.line_price_incl_tax for line in lines)

                # Request was successful - record the "payment source".  As this
                # request was a 'pre-auth', we set the 'amount_allocated' - if we had
                # performed an 'auth' request, then we would set 'amount_debited'.
                source = Source(source_type=source_type,
                                currency='BRL',
                                amount_debited=total,
                                reference=transaction_id)
                # When we create a transaction, we have to set a txn_type that should be debit or refund
                source.create_deferred_transaction("akatus-creditcard-init", total, reference=transaction_id, status=1,
                                                   bankcard=bankcard)
                self.add_payment_source(source)

                # Also record payment event
                # When we create the payment event, we have to set a txn_type that should be debit or refund
                self.add_payment_event('akatus-creditcard-init', total, reference=transaction_id, lines=lines)

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

        source.create_deferred_transaction("akatus-boleto-init", total_incl_tax.incl_tax, reference=transaction_id,
                                           status=1, boleto=boleto)
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

        # Se o ambiente for de testes, vamos setar o pedido como pago
        if settings.AKATUS_ENVIRONMENT == 'TST':
            order.set_status('Pago')
            for line in order.lines.all():
                line.set_status('Pago')

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


class StatusChangedView(TemplateView, PaymentEventMixin):
    template_name = 'checkout/akatus/status_changed.html'
    _payment_events = None

    def post(self, request, *args, **kwargs):
        log.info('AKATUS STATUS CHANGED POST: {}'.format(self.request.POST))

        token = self.request.POST.get('token')

        if token != settings.AKATUS_TOKEN_NIP:
            log.warning('chamada ao akatus status changed com token inválido')
            raise Http404()

        order_number = self.request.POST['referencia']
        transacao_id = self.request.POST['transacao_id']
        status = self.request.POST['status']

        log.info('Order #{} com transaction_id {} alterou o status para {}'.format(order_number, transacao_id, status))

        # Implementação de um timer que previne a Akatus atualizar o status antes de terminar de criar o objeto Order:
        order = None
        for n in range(1, 10):
            try:
                order = Order.objects.get(number=order_number) if order_number else None
            except Order.DoesNotExist:
                log.info('Order #{} ainda não criada no sistema'.format(order_number, transacao_id, status))
                sleep(n)
                continue
            break
        if not order:
            log.error('Order #{} não foi atualizada para {} por não existir ainda no sistema'.format(order_number,
                                                                                                     status))
            return self.get(request, *args, **kwargs)

        if status == 'Aprovado':
            try:
                lines = order.lines.filter(paymentevent_set__reference=transacao_id)

                for line in lines:
                    line.set_status('Pago')

                if order.lines.count() == order.lines.filter(status='Pago').count():
                    order.set_status('Pago')
                    subject = 'Pagamento Aprovado'
                    template = 'customer/commtype_order_placed_body.html'
                    context = {
                        'user': order.user,
                        'order': order,
                        'site': get_current_site(self.request),
                        'lines': order.lines.all()
                    }
                    send_template_email([order.user.email], subject, template, context)

                if lines:
                    event = lines[0].paymentevent_set.all()[0]
                    self.add_payment_event('akatus-approved', event.amount, reference=transacao_id, lines=lines)
                    self.save_payment_events(order)
            except Order.DoesNotExist:
                log.error('Não encontrou a order #{}'.format(order_number))
            except Line.DoesNotExist:
                log.error('Não encontrou a line com partner_line_reference={} da order #{}'.format(transacao_id, order_number))
        else:
            profile = order.user.get_profile()
            message = 'número do pedido: %s \n CNPJ: %s \n razão social: %s \n valor do pedido: %s \n status: %s' % (
                order_number, profile.cliente_cnpj, profile.cliente_razaosocial, order.total_incl_tax, status
            )
            send_mail('[Alerta-Akatus] Alteração de status não prevista para ordem #%s: %s' % (order_number, status),
                      message,
                      settings.DEFAULT_FROM_EMAIL,
                      [settings.TRUSTSIGN_SUPORTE_EMAIL])

        return self.get(request, *args, **kwargs)