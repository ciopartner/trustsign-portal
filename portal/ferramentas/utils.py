# coding=utf-8
import commands
from difflib import get_close_matches
import re
import urllib
import urlparse
import requests
from unicodedata import normalize
from nltk import metrics


def decode_csr(csr, show_key_size=True, show_csr_hashes=True, show_san_dns=True):
    """
    Retorna um dict com os campos decodificados da CSR conforme abaixo:

    CN=xxxxx > Common Name
    OU=xxxxx > Organizational Unit Name
    O=xxxxx > Organization Name
    POBox=xxxxx > Post Office Box
    STREET1=xxxxx > Street Address 1
    STREET2=xxxxx > Street Address 2
    STREET3=xxxxx > Street Address 3
    L=xxxxx > Locality Name
    S=xxxxx > State or Province Name
    PostalCode=xxxxx > Postal Code
    C=xxxxx > Country Name
    Email=xxxxx > Email Address
    Phone=xxxxx > Telephone Number
    PublicKey=xxxxx > Public Key
    KeySize=xxxxx > Key Size (in bits)
    dnsNames=xxxxx,yyyy,zzzzz,etc,etc > Subject Alternative Name dnsName(s)
    md5=xxxxx > MD5 Hash of DER-encoded CSR
    sha1=xxxxx > SHA-1 Hash of DER-encoded CSR

    ok=xxxxx > Valida se houve erros na decodificação
    subject_ok=xxxxx > Valida se CN, O, L, S, C estão preenchidos
    """

    response = requests.post('https://secure.comodo.net/products/!DecodeCSR', {
        'csr': csr,
        'showKeySize': 'Y' if show_key_size else 'N',
        'showCSRHashes': 'Y' if show_csr_hashes else 'N',
        'showSANDNSNames': 'Y' if show_san_dns else 'N'
    })

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
            if key == 'STREET':  # tem 3 STREET na resposta então coloca um indice pra nao sobrescrever no dict
                key = '%s%d' % (key, street_index)
                street_index += 1
            if key == 'dnsName(s)':
                key = 'dnsNames'
                value = map(lambda x: x.strip(), value.split())

            d[key.replace(' ', '')] = value

    d['subject_ok'] = d.get('CN') and d.get('O') and d.get('L') and d.get('S') and d.get('C')

    return d


def get_razao_social_dominio(dominio):
    razao_social = commands.getoutput('whois %s | grep ^owner:' % dominio).strip()
    r = re.match('owner:\s*(.+)', razao_social)
    if r:
        return r.groups()[0]
    return None


def remove_acentos(txt, codif='utf-8'):
    return normalize('NFKD', txt.decode(codif)).encode('ASCII','ignore')


def comparacao_fuzzy(string1, string2, max_dist=5):
    """
    Faz a comparação de duas strings usando o parâmetro max_dist como distância máxima (número de caracteres que
    precisam ser substituidos, removidos ou adicionados de string1 para chegar em string2)
    """
    return metrics.edit_distance(remove_acentos(string1).lower(), remove_acentos(string2).lower()) <= max_dist


def verifica_razaosocial_dominio(razao_social, emissao_url):
    razaosocial_dominio = get_razao_social_dominio(emissao_url)
    return razaosocial_dominio and comparacao_fuzzy(razaosocial_dominio, razao_social)


def url_parse(url):
    resultado = urlparse.parse_qs(urllib.unquote(url))  # transforma em um dict os dados recebidos
    return dict((k, v[0])for k, v in resultado.iteritems())  # tira os valores da lista