# coding=utf-8
from Crypto.Util import asn1
from datetime import date
import urllib
import urlparse
import OpenSSL
from django.core.exceptions import ValidationError
from django.forms import Form, CharField, HiddenInput, Textarea, FileField, ChoiceField, PasswordInput
import requests
from hashlib import md5


def string_to_date(valor):
    print valor
    print date(int(valor[:4]), int(valor[4:6]), int(valor[6:8]))
    print '------'
    return date(int(valor[:4]), int(valor[4:6]), int(valor[6:8]))


def altera_datas(d, chaves):
    """
    Recebe um dict e a lista de chaves que é para transformar em datetime.date
    """
    for k in chaves:
        d[k] = string_to_date(d[k])


class SSLCheckerError(Exception):
    pass


class SSLCheckerForm(Form):

    url = CharField()
    operation = CharField(widget=HiddenInput, initial='ssl-checker')

    def processa(self):

        url = self.cleaned_data['url']
        response = requests.post('https://secure.comodo.com/sslchecker', {
            'url': url
        })
        resultado = urlparse.parse_qs(urllib.unquote(response.text))  # transforma em um dict os dados recebidos
        resultado = dict((k, v[0])for k, v in resultado.iteritems())  # tira os valores da lista

        resultado['ok'] = ok = int(resultado.get('error_code', 0)) == 0
        if ok:
            altera_datas(resultado, ('cert_validity_notBefore', 'cert_validity_notAfter', ))
            resultado['expira_em'] = (resultado['cert_validity_notAfter'] - date.today()).days
            resultado['hostname_listado'] = url in resultado.get('cert_san_1_dNSName') or url in resultado.get('cert_san_2_dNSName')

        return resultado


class CSRDecodeError(Exception):
    def __init__(self, erros, *args, **kwargs):
        self.erros = erros
        super(CSRDecodeError, self).__init__(*args, **kwargs)


class CSRDecoderForm(Form):

    csr = CharField(widget=Textarea)
    operation = CharField(widget=HiddenInput, initial='csr-decoder')

    def processa(self):
        csr = self.cleaned_data['csr']
        response = requests.post('https://secure.comodo.net/products/!DecodeCSR', {
            'csr': csr
        })

        print response.text

        d = {}
        street_index = 1
        linhas = response.text.splitlines()
        # erro -13 e quando o certificado esta incompleto, mas da pra exibir alguns campos mesmo assim
        erros = [linhas[i + 1] for i in range(int(linhas[0])) if not linhas[i + 1].startswith('-13')]
        d['ok'] = not erros

        for linha in linhas:
            x = linha.split('=')
            if len(x) == 2:
                key, value = x
                if key == 'STREET':  # tem 3 STREET na resposta
                    key = '%s%d' % (key, street_index)
                    street_index += 1
                d[key] = value

        return d


class CertificateKeyMatcherForm(Form):

    certificado = FileField()
    private_key = FileField()
    operation = CharField(widget=HiddenInput, initial='certificate-key-matcher')

    def processa(self):
        # source: http://www.v13.gr/blog/?p=325

        certificate = self.cleaned_data['certificado'].read()
        private_key = self.cleaned_data['private_key'].read()

        c = OpenSSL.crypto

        pub = c.load_certificate(c.FILETYPE_PEM, certificate).get_pubkey()
        priv = c.load_privatekey(c.FILETYPE_PEM, private_key)

        if pub.type() != c.TYPE_RSA or priv.type() != c.TYPE_RSA:
            raise Exception('Can only handle RSA keys')

        pub_asn1 = c.dump_privatekey(c.FILETYPE_ASN1, pub)
        priv_asn1 = c.dump_privatekey(c.FILETYPE_ASN1, priv)

        pub_der = asn1.DerSequence()
        pub_der.decode(pub_asn1)

        priv_der = asn1.DerSequence()
        priv_der.decode(priv_asn1)

        pub_modulus = pub_der[1]
        priv_modulus = priv_der[1]

        return {
            'ok': True,
            'match': pub_modulus == priv_modulus,
            'modulus_certificado': md5('Modulus=%s\n' % hex(pub_modulus)[2:-1].upper()).hexdigest(),
            'modulus_key': md5('Modulus=%s\n' % hex(priv_modulus)[2:-1].upper()).hexdigest(),
        }


class SSLConverterForm(Form):

    STANDARD_PEM = 1
    DER_BINARY = 2
    P7B_PKCS_7 = 3
    PFX_PKCS_12 = 4
    TIPO_CHOICES = (
        (STANDARD_PEM, 'Standard PEM'),
        (DER_BINARY, 'DER/Binary'),
        (P7B_PKCS_7, 'P7B/PKCS#7'),
        (PFX_PKCS_12, 'PFX/PKCS#12'),
    )

    certificado = FileField()
    tipo_atual = ChoiceField(choices=TIPO_CHOICES)
    tipo_para_coverter = ChoiceField(choices=TIPO_CHOICES)
    pfx_password = CharField(widget=PasswordInput)
    operation = CharField(widget=HiddenInput, initial='ssl-converter')

    def clean(self):
        tipo_atual = self.cleaned_data['tipo_atual']
        tipo_para_converter = self.cleaned_data['tipo_para_converter']

        if tipo_atual == tipo_para_converter:
            raise ValidationError(u'Os tipos precisam ser diferentes')

        return self.cleaned_data

    def processa(self):
        certificado = self.cleaned_data['certificado']
        tipo_atual = self.cleaned_data['tipo_atual']
        tipo_para_converter = self.cleaned_data['tipo_para_converter']


        return

    def converte_pem_der(self, certificado):
        pass

    def converte_pem_p7(self, certificado):
        pass

    def converte_pem_p12(self, certificado):
        pass

    def converte_pem_der(self, certificado):
        pass

    def converte_pem_p7(self, certificado):
        pass

    def converte_pem_p12(self, certificado):
        pass