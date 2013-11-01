# -*- coding: utf-8 -*-

import urllib
import requests
import xml.etree.ElementTree as ET
from django.conf import settings

class Response(object):
    """
    This class is responsible for assemble the gateway response
    """

    def __init__(self, request_url, response_xml, extract_data):
        self.request_url = request_url
        self.response_xml = response_xml
        self.data = getattr(self,extract_data)(response_xml)
        
    def _extract_data_approval(self, response_xml):        
        doc = ET.fromstring(response_xml.encode("utf-8"))                
        data = {'transacao_aprovada': doc.find('TransacaoAprovada').text,
                'resultado_solicitacao_aprovacao': doc.find('ResultadoSolicitacaoAprovacao').text,
                'codigo_autorizacao': doc.find('CodigoAutorizacao').text,
                'transacao': doc.find('Transacao').text,                
                }        
        return data

    def _extract_data_capture(self, response_xml):
        doc = ET.fromstring(response_xml.encode("utf-8"))         
        data = {'resultado_solicitacao_confirmacao': doc.find('ResultadoSolicitacaoConfirmacao').text,
                'comprovante_administradora': doc.find('ComprovanteAdministradora').text,                          
                }                      
        return data
    
    def _extract_data_cancel(self, response_xml):
        doc = ET.fromstring(response_xml.encode("utf-8"))         
        data = {'resultado_solicitacao_cancelamento': doc.find('ResultadoSolicitacaoCancelamento').text,                
                'nsu_cancelamento': doc.find('NSUCancelamento').text,                          
                }
        data['resultado_solicitacao_cancelamento'] = 'Cancelamento marcado para envio %s' % data['resultado_solicitacao_cancelamento'].split(" ")[-1]                     
        return data

    def _get_element_text(self, doc, tag):
        try:
            ele = doc.getElementsByTagName(tag)[0]
        except IndexError:
            return None
        return ele.firstChild.data

    def __getitem__(self, key):
        return self.data[key]

    def __contains__(self, key):
        return key in self.data

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.response_xml

    @property
    def cobrebem_reference(self):
        return self.data['cobrebem_reference']

    def is_successful(self):        
        return self.data.get('transacao_aprovada', None) == "True"

    def is_declined(self):
        return self.data.get('transacao_aprovada', None) == "False"


class Gateway(object):
    """
    This is an abstract class
    """
    # Used webservice methods
    APPROVAL = 'APC'
    CAPTURE = 'CAP'
    CANCEL = 'CAN'
    BOLETO = 'BOL'
    DEBITO = 'TRX'

    def __init__(self):
        self._host = settings.COBREBEM_HOST
        self._path = settings.COBREBEM_USER

class CreditCard(Gateway):
    """
    This class is responsible for the gateway integration.
    """
    def _do_request_post(self, method_name, extract_data_type, params):
        url = "/".join([self._host, self._path, method_name])        
        params = urllib.urlencode(params)
        req = requests.post(url, params=params)
        response = Response(req.url, req.text, extract_data_type)
        return response        

    def approval(self, **kwargs):
        credito_args = {}
        credito_args['NumeroDocumento'] = kwargs.get('order_number')
        credito_args['QuantidadeParcelas'] = "01"
        credito_args['ValorDocumento'] = kwargs.get('amount')
        credito_args['NumeroCartao'] = kwargs.get('card_number')
        credito_args['MesValidade'] = kwargs.get('expiry_date').strftime("%m")
        credito_args['AnoValidade'] = kwargs.get('expiry_date').strftime("%y")
        credito_args['CodigoSeguranca'] = kwargs.get('ccv')
        credito_args['EnderecoIPComprador'] = kwargs.get('ip')
        return self._do_request_post(self.APPROVAL, "_extract_data_approval", params=credito_args)

    def capture(self, **kwargs):
        capture={}
        capture['Transacao']  = kwargs['transaction']
        return self._do_request_post(self.CAPTURE, "_extract_data_capture", capture)

    def cancel(self, **kwargs):
        cancel = {}
        cancel['Transacao']  = kwargs['transaction']
        return self._do_request_post(self.CANCEL, "_extract_data_cancel", cancel)

class Boleto(Gateway):
    """
    This class is responsible for the integration with Boleto.
    """
    def _do_request_post(self, method_name, extract_data_type, params):
        url = "/".join([self._host, self._path, method_name])
        params = urllib.urlencode(params)
        response = requests.get(url, params=params)
        return response

    def get_boleto(self, **kwargs):
        boleto_args = {}
        boleto_args['CCID'] = '341-3777'
        boleto_args['NumeroDocumento'] = kwargs.get('order_number')
        boleto_args['ValorDocumento'] = kwargs.get('amount')
        #boleto_args['DataVencimento'] = 'aaaammdd' usar PrazoVencimento instead of
        boleto_args['PrazoVencimento'] = '03'
        boleto_args['VencimentoDiaUtil'] = 'S'

        # Dados do Sacado
        boleto_args['CNPJCPFSacado'] = '08.886.686/0001-71'.replace('.', '').replace('/', '').replace('-', '')
        boleto_args['NomeSacado'] = 'Reichert Consultoria em Informática LTDA'
        boleto_args['EnderecoSacado'] = ''
        boleto_args['CEPSacado'] = ''
        boleto_args['CidadeSacado'] = ''
        boleto_args['EstadoSacado'] = ''
        boleto_args['EnderecoEmailSacado'] = ''

        # Outros Dados:
        #boleto_args['PercentualJurosDia'] = '0,03%'
        #boleto_args['PercentualMulta'] = '2%'
        boleto_args['InstrucoesCaixa'] = 'Não receber após o vencimento'
        boleto_args['EspecieDocumento'] = 'DM'
        boleto_args['Demonstrativo'] = 'Título referente ao pedido {}'.format(kwargs.get('order_number'))

        return self._do_request_post(self.BOLETO, "_extract_data_boleto_args", params=boleto_args)

class DebitCard(Gateway):
    """
    This class is responsible for the integration with Boleto.
    """
    BB = 'BBRASIL'
    BANRISUL = 'BANRISUL'
    BRADESCO = 'BRADESCO'
    ITAU = 'ITAU'
    HSBC = 'HSBC'

    def _do_request_post(self, method_name, extract_data_type, params):
        url = "/".join([self._host, self._path, method_name])
        params = urllib.urlencode(params)
        response = requests.post(url, data=params)
        return response

    def get_page(self, **kwargs):
        debito_args = {}
        debito_args['NumeroDocumento'] = kwargs.get('order_number')
        debito_args['QuantidadeParcelas'] = '01'
        debito_args['ValorDocumento'] = kwargs.get('amount')
        debito_args['Bandeira'] = self.BRADESCO
        debito_args['CNPJCPFSacado'] = '08.886.686/0001-71'.replace('.', '').replace('/', '').replace('-', '')

        return self._do_request_post(self.DEBITO, "_extract_data_debito_args", params=debito_args)