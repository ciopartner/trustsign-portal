# coding=utf-8
from __future__ import unicode_literals
from datetime import date
import os
import urllib
from hashlib import md5

from Crypto.Util import asn1
import OpenSSL
from OpenSSL.crypto import load_certificate, FILETYPE_PEM, dump_certificate, FILETYPE_ASN1, load_pkcs12, PKCS12, dump_privatekey, load_privatekey
from django.core.exceptions import ValidationError
from django.core.files.temp import NamedTemporaryFile
from django.forms import Form, CharField, HiddenInput, Textarea, FileField, ChoiceField, PasswordInput, TextInput
import requests

from portal.suporte.utils import decode_csr, url_parse, run_command


def string_to_date(valor):
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

    url = CharField(label='URL', widget=TextInput(attrs={'class': 'span5'}))
    operation = CharField(widget=HiddenInput, initial='ssl-checker')

    def processa(self):

        url = self.cleaned_data['url']
        response = requests.post('https://secure.comodo.com/sslchecker', {
            'url': url
        })
        resultado = url_parse(response.text)

        resultado['ok'] = ok = int(resultado.get('error_code', 0)) == 0
        if ok:
            altera_datas(resultado, ('cert_validity_notBefore', 'cert_validity_notAfter', ))
            resultado['expira_em'] = (resultado['cert_validity_notAfter'] - date.today()).days

            resultado['cert_subject_DN'] = urllib.unquote(resultado['cert_subject_DN']).replace('\\r\\n', '\r\n')
            resultado['cert_issuer_DN'] = urllib.unquote(resultado['cert_issuer_DN']).replace('\\r\\n', '\r\n')

        sans = []
        site_listed = False
        url_wildcard = '.'.join(['*'] + url.split('.')[1:])
        for k, v in resultado.iteritems():
            if k.startswith('cert_san_'):
                if v in (url, url_wildcard):
                    site_listed = True
                sans.append(v)

        resultado['cert_sans'] = ', '.join(sans)
        resultado['site_listed'] = site_listed
        return resultado


class CSRDecodeError(Exception):
    pass


class CSRDecoderForm(Form):

    csr = CharField(label='CSR', widget=Textarea(attrs={'class': 'span5'}))
    operation = CharField(widget=HiddenInput, initial='csr-decoder')

    def processa(self):
        csr = decode_csr(self.cleaned_data['csr'])
        if not csr['ok']:
            raise CSRDecodeError()
        return csr


class CertificateKeyMatcherForm(Form):

    certificado = FileField()
    private_key = FileField(label='Chave Privada')
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
    private_key = FileField(required=False, label='Chave Privada')
    tipo_atual = ChoiceField(choices=TIPO_CHOICES, label='Formato Entrada')
    tipo_para_converter = ChoiceField(choices=TIPO_CHOICES, label='Formato Saída')
    pfx_password = CharField(widget=PasswordInput, required=False)
    operation = CharField(widget=HiddenInput, initial='ssl-converter')

    def clean(self):
        tipo_atual = self.cleaned_data['tipo_atual']
        tipo_para_converter = self.cleaned_data['tipo_para_converter']

        if tipo_atual == tipo_para_converter:
            raise ValidationError('Os tipos precisam ser diferentes')

        return self.cleaned_data

    def processa(self):
        certificado = self.cleaned_data['certificado'].read()
        private_key = self.cleaned_data['private_key']
        if private_key:
            private_key = private_key.read()
        tipo_atual = int(self.cleaned_data['tipo_atual'])
        tipo_para_converter = int(self.cleaned_data['tipo_para_converter'])
        password = self.cleaned_data['pfx_password']

        # PEM -> X
        if tipo_atual == self.STANDARD_PEM:
            if tipo_para_converter == self.DER_BINARY:
                return self.converte_pem_der(certificado)
            if tipo_para_converter == self.P7B_PKCS_7:
                return self.converte_pem_p7(certificado)
            return self.converte_pem_p12(certificado, private_key, password)

        # DER -> X
        if tipo_atual == self.DER_BINARY:
            if tipo_para_converter == self.STANDARD_PEM:
                return self.converte_der_pem(certificado)
            if tipo_para_converter == self.P7B_PKCS_7:
                return self.converte_pem_p7(self.converte_der_pem(certificado))
            return self.converte_pem_p12(self.converte_der_pem(certificado), private_key, password)

        # P7 -> X
        if tipo_atual == self.P7B_PKCS_7:
            if tipo_para_converter == self.STANDARD_PEM:
                return self.converte_p7_pem(certificado)
            if tipo_para_converter == self.DER_BINARY:
                return self.converte_pem_der(self.converte_p7_pem(certificado))
            return self.converte_pem_p12(self.converte_p7_pem(certificado), private_key, password)

        # P12 -> X
        if tipo_para_converter == self.STANDARD_PEM:
            return self.converte_p12_pem(certificado, password)
        if tipo_para_converter == self.DER_BINARY:
            return self.converte_pem_der(self.converte_p12_pem(certificado, password))
        return self.converte_pem_p7(self.converte_p12_pem(certificado, password))

    def converte_pem_der(self, certificado):
        cert = load_certificate(FILETYPE_PEM, certificado)
        return dump_certificate(FILETYPE_ASN1, cert)

    def converte_pem_p7(self, certificado):
        file_in = NamedTemporaryFile(delete=False)
        file_in.write(certificado)
        path_in = file_in.name
        file_in.close()
        # Como a biblioteca PyOpenSSL não trata pkcs7, é usado a própria openssl do linux.
        cert = run_command('openssl crl2pkcs7 -nocrl -certfile %s' % path_in)
        os.remove(path_in)
        return cert

    def converte_pem_p12(self, certificado, private_key, password):
        p12 = PKCS12()
        cert = load_certificate(FILETYPE_PEM, certificado)
        p12.set_certificate(cert)
        if private_key:
            priv = load_privatekey(FILETYPE_PEM, private_key)
            p12.set_privatekey(priv)
        return p12.export(password, iter=2, maciter=3)

    def converte_der_pem(self, certificado):
        cert = load_certificate(FILETYPE_ASN1, certificado)
        return dump_certificate(FILETYPE_PEM, cert)

    def converte_p7_pem(self, certificado):
        file_in = NamedTemporaryFile(delete=False)
        file_in.write(certificado)
        path_in = file_in.name
        file_in.close()
        # Como a biblioteca PyOpenSSL não trata pkcs7, é usado a própria openssl do linux.
        cert = run_command('openssl pkcs7 -print_certs -in %s' % path_in)
        os.remove(path_in)
        return cert

    def converte_p12_pem(self, certificado, password):
        p12 = load_pkcs12(certificado, password)
        return dump_certificate(FILETYPE_PEM, p12.get_certificate()) + \
            dump_privatekey(FILETYPE_PEM, p12.get_privatekey())
