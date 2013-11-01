# -*- coding: utf-8 -*-

from django.conf import settings
from oscar.apps.payment.exceptions import UnableToTakePayment, InvalidGatewayRequestError
from libs.cobrebem.exceptions import UnableToCancelTransaction
from libs.cobrebem.gateway import Boleto, CreditCard


class Facade(object):
    """
    Classe de Fachada
    """

    def handle_response(self, method, order_number, amount, response):
        #self.record_txn(method, order_number, amount, response)
        # A response is either successful, declined or an error        
        if response.is_successful():
            return response['transacao']
        elif response.is_declined():
            msg = self.get_friendly_decline_message(response)
            raise UnableToTakePayment(msg)
    
    def get_friendly_decline_message(self, msg):
        return u'Ocorreu um erro durante o pagamento: %s ' % msg

    def approval(self, request, order_number, amount, bankcard):
        """
        This method requests CobreBem Approval for Credit Card.
        You must call the capture method to confirm the transaction.
        """
        ip = request.META['REMOTE_ADDR']
        gateway = CreditCard()

        if amount == 0:
            raise UnableToTakePayment("Order amount must be non-zero")
        response = gateway.approval(
                order_number=order_number,
                card_number=bankcard.number,
                expiry_date=bankcard.expiry_date,
                amount=amount,                                
                ccv=bankcard.ccv,
                ip=ip)             
        if response.is_successful():
            transaction_id = response['transacao']
            return transaction_id
        msg = self.get_friendly_decline_message(response['resultado_solicitacao_aprovacao'])
        raise UnableToTakePayment(msg)

    def capture(self, transaction):
        """
        This method confirms the approved amount to be debited.
        Without calling this method the amount will not be charged.
        """
        gateway = CreditCard()
        response = gateway.capture(transaction=transaction)
        if response['resultado_solicitacao_confirmacao'].startswith("Erro"):
            msg = self.get_friendly_decline_message(response['resultado_solicitacao_confirmacao'])
            raise UnableToTakePayment(msg)                
        return response['resultado_solicitacao_confirmacao'].split('Confirmado ')[1].rstrip()

    def cancel(self, transaction):
        gateway = CreditCard()
        response = gateway.cancel(transaction=transaction)
        if response['resultado_solicitacao_cancelamento'].startswith("Erro"):
            raise UnableToCancelTransaction(response['resultado_solicitacao_cancelamento'])
        return response['resultado_solicitacao_cancelamento']

    def get_boleto(self, request, order_number, amount):
        gateway = Boleto()
        return gateway.get_boleto(
                order_number = order_number,
                amount = amount,
        )

    def debit_card(self, request, order_number, amount, bank):
        gateway = CreditCard()
        ip = request.META['REMOTE_ADDR']
        pass