# -*- coding: utf-8 -*-

from django.conf import settings
from oscar.apps.payment.exceptions import UnableToTakePayment, InvalidGatewayRequestError
from libs.cobrebem.exceptions import UnableToCancelTransaction
from libs.cobrebem import gateway


class Facade(object):

    def __init__(self):
        self.gateway = gateway.Gateway(
            settings.COBREBEM_HOST,
            settings.COBREBEM_USER)
        
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

    def approval(self,order_number, amount, bankcard, ip):
        if amount == 0:
            raise UnableToTakePayment("Order amount must be non-zero")
        response = self.gateway.approval(
                card_number=bankcard.card_number,
                expiry_date=bankcard.expiry_date,
                amount=amount,                                
                ccv=bankcard.ccv,
                ip=ip)             
        if response.is_successful():            
            return self.capture(response['transacao'])
        else:
            msg = self.get_friendly_decline_message(response['resultado_solicitacao_aprovacao'])
            raise UnableToTakePayment(msg)

    def capture(self, transaction):
        response = self.gateway.capture(transaction=transaction)
        if response['resultado_solicitacao_confirmacao'].startswith("Erro"):
            msg = self.get_friendly_decline_message(response['resultado_solicitacao_confirmacao'])
            raise UnableToTakePayment(msg)                
        return response['resultado_solicitacao_confirmacao'].split('Confirmado ')[1].rstrip()

    def cancel(self, transaction):
        response = self.gateway.cancel(transaction=transaction)
        if response['resultado_solicitacao_cancelamento'].startswith("Erro"):
            raise UnableToCancelTransaction(response['resultado_solicitacao_cancelamento'])
        return response['resultado_solicitacao_cancelamento']
