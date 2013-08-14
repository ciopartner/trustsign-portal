# coding=utf-8
from Crypto.Util import asn1
import urllib
import urlparse
import OpenSSL
from django.core.exceptions import ValidationError
from django.forms import Form, CharField, HiddenInput, Textarea, FileField, ChoiceField, PasswordInput
import requests


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
        d = urlparse.parse_qs(urllib.unquote(response.text))  # transforma em um dict todos os parametros recebidos
        d = dict((k, v[0])for k, v in d.iteritems())  # tira os valores da lista
        print d

        if int(d.get('error_code', 0)) != 0:
            raise SSLCheckerError(d.get('error_message'))

        return d


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

        d = {}
        street_index = 1
        linhas = response.text.splitlines()

        erros = [linhas[i + 1] for i in range(int(linhas[0]))]
        if erros:
            raise CSRDecodeError(erros)

        for linha in linhas:
            x = linha.split('=')
            if len(x) == 2:
                key, value = x
                if key == 'STREET':  # tem 3 STREET na resposta
                    key += street_index
                    street_index += 1
                d[key] = value

        return d


class CertificateKeyMatcherForm(Form):

    certificado = FileField()
    private_key = FileField()
    operation = CharField(widget=HiddenInput, initial='certificate-key-matcher')

    def processa(self):
        # source: http://www.v13.gr/blog/?p=325

        certificate = self.cleaned_data['certificado']
        private_key = self.cleaned_data['private_key']

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

        return pub_modulus == priv_modulus


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