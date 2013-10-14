# -*- coding: utf-8 -*-

import urllib
import requests
import xml.etree.ElementTree as ET

# Methods
APPROVAL = 'APC'
CAPTURE = 'CAP'
CANCEL = 'CAN'

class Response(object):
    """
    Encapsulate a Cobrebem response
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

    def __init__(self, host, path):        
        self._host = host
        self._path = path

    def _do_request_post(self, method_name, extract_data_type, **kwargs):
        url = "/".join([self._host, self._path, method_name])        
        params = urllib.urlencode(kwargs)        
        req = requests.post(url,params=params)        
        response = Response(req.url, req.text, extract_data_type)
        return response        

    def approval(self, **kwargs):        
        kwargs['QuantidadeParcelas'] = "01"        
        kwargs['ValorDocumento'] = kwargs['amount']
        kwargs['NumeroCartao'] = kwargs['card_number']
        kwargs['MesValidade'] = kwargs['expiry_date'].strftime("%m")
        kwargs['AnoValidade'] = kwargs['expiry_date'].strftime("%y")        
        kwargs['CodigoSeguranca'] = kwargs['ccv']
        kwargs['EnderecoIPComprador'] = kwargs['ip']
        del kwargs['ip']
        del kwargs['ccv']
        del kwargs['card_number']
        del kwargs['expiry_date']
        del kwargs['amount']        
        return self._do_request_post(APPROVAL, "_extract_data_approval", **kwargs)

    def capture(self, **kwargs):
        kwargs['Transacao']  = kwargs['transaction']        
        del kwargs['transaction']
        return self._do_request_post(CAPTURE, "_extract_data_capture", **kwargs)

    def cancel(self, **kwargs):
        kwargs['Transacao']  = kwargs['transaction']        
        del kwargs['transaction']
        return self._do_request_post(CANCEL, "_extract_data_cancel", **kwargs)

    
