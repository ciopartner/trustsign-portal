# coding: utf-8
from __future__ import unicode_literals

from dateutil import parser
from django.core.files.temp import NamedTemporaryFile
from subprocess import Popen, PIPE
import re
import os


pattern_serial_number = r'(?=.*?Serial Number: (.*?$))?'
pattern_subject = r'(?=.*?Subject: (?=.*?C=(.*?)(?:,|$|/))?(?=.*?ST?=(.*?)(?:,|$|/))?(?=.*?L=(.*?)(?:,|$|/))?(?=.*?O=(.*?)(?:,|$|/))?(?=.*?OU=(.*?)(?:,|$|/))?(?=.*?CN=(.*?)(?:,|$|/))?)?'
pattern_issuer = r'(?=.*?Issuer: (?=.*?C=(.*?)(?:,|$|/))?(?=.*?ST?=(.*?)(?:,|$|/))?(?=.*?L=(.*?)(?:,|$|/))?(?=.*?O=(.*?)(?:,|$|/))?(?=.*?OU=(.*?)(?:,|$|/))?(?=.*?CN=(.*?)(?:,|$|/))?)?'
pattern_validity = r'(?=.*?Validity\s*Not Before: (.*?$)\s*Not After : (.*?$))?'
pattern_key_size = r'(?=.*?Public-Key: \((\d+) bit\))?'
pattern_signature = r'(?=.*?Signature Algorithm: (.*?$))?'
pattern_modulus = r'(?=.*?Modulus:\s+?((?:(?::\s*?)?[0-9a-fA-F]{2})+)$)?'
pattern_dns = r'(?=.*?Subject Alternative Name:\s+(DNS:.*?(:,\s|$))+)?'

pattern_completa = pattern_serial_number + pattern_subject + pattern_issuer + pattern_validity + pattern_key_size + pattern_signature + pattern_modulus + pattern_dns
pattern_completa = re.compile(pattern_completa, flags=re.MULTILINE | re.DOTALL)


class SSLCertificateDecodeError(Exception):
    pass


def cria_arquivo_temporario(conteudo, delete=False):
    file_in = NamedTemporaryFile(delete=delete)
    file_in.write(conteudo)
    path_in = file_in.name
    file_in.close()

    return path_in


def run_command(comando):
    p = Popen(comando, shell=True, stdin=PIPE, stdout=PIPE, close_fds=True)
    (write, read) = (p.stdin, p.stdout)
    write.close()

    return read.read()


def certificate_decode(raw_certificado):

    path_in = cria_arquivo_temporario(raw_certificado)

    if 'PKCS7' in raw_certificado:
        certificado = run_command('openssl pkcs7 -in {} -print_certs -text -noout'.format(path_in))
    else:
        certificado = run_command('openssl x509 -in {} -text -noout'.format(path_in))

    os.remove(path_in)

    m = re.match(pattern_completa, certificado)
    if m:
        g = m.groups()
        if any(g):
            if g[18]:
                dns = [d.replace('DNS:', '') for d in g[18].split(', ')]
            else:
                dns = None
            return {
                'serial_number': g[0],
                'subject': {
                    'C': g[1],
                    'ST': g[2],
                    'L': g[3],
                    'O': g[4],
                    'OU': g[5],
                    'CN': g[6],
                },
                'issuer': {
                    'C': g[7],
                    'ST': g[8],
                    'L': g[9],
                    'O': g[10],
                    'OU': g[11],
                    'CN': g[12],
                },
                'validity':{
                    'not_before': parser.parse(g[13]) if g[13] is not None else None,
                    'not_after': parser.parse(g[14]) if g[14] is not None else None,
                },
                'key_size': g[15],
                'signature': g[16],
                'modulus': g[17].replace(' ', '') if g[17] is not None else None,
                'dns': dns
            }

    raise SSLCertificateDecodeError