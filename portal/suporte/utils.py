# coding=utf-8
import commands
import re
import os
from subprocess import Popen, PIPE
import urllib
import urlparse
from django.core.files.temp import NamedTemporaryFile
from django.utils.encoding import smart_unicode
import requests
from unicodedata import normalize
from nltk import metrics
from logging import getLogger
from ecommerce.certificados.crons import chunks


log = getLogger('portal.suporte.utils')


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

regex_c = re.compile(r'C=(.+?)([,/] (.+?=)|$)')
regex_st = re.compile(r'ST=(.+?)([,/] (.+?=)|$)')
regex_l = re.compile(r'L=(.+?)([,/] (.+?=)|$)')
regex_o = re.compile(r'O=(.+?)([,/] (.+?=)|$)')
regex_ou = re.compile(r'OU=(.+?)([,/] (.+?=)|$)')
regex_cn = re.compile(r'CN=(.+?)([,/] (.+?=)|$)')
regex_email = re.compile(r'emailAddress=(.+?)([,/] (.+?=)|$)')

pattern_csr = r'-----BEGIN .*?CERTIFICATE REQUEST-----(.*)-----END .*?CERTIFICATE REQUEST-----'
regex_csr = re.compile(pattern_csr, flags=re.DOTALL | re.MULTILINE)


def decode_csr(csr):

    d = {
        'POBox': '',
        'STREET1': '',
        'STREET2': '',
        'STREET3': '',
        'PostalCode': '',
        'Phone': '',
        'KeySize': 0,
        'dnsNames': [],
        'ok': True,

    }

    m = re.match(regex_csr, csr)  # retira ---- begin/end certificate request ----
    if not m:
        return {
            'ok': False
        }
    clean_csr = re.sub(r'\s', '', m.groups()[0])  # retira espaços e quebras de linha
    clean_csr = '\n'.join(chunks(clean_csr, 64))  # quebra em linhas de 64 chars
    clean_csr = '-----BEGIN CERTIFICATE REQUEST-----\n{}\n-----END CERTIFICATE REQUEST-----'.format(clean_csr)

    path_in = cria_arquivo_temporario(clean_csr)

    resposta = run_command('openssl req -in %s -noout -text | grep "DNS\|Subject:\|Key:"' % path_in)

    os.remove(path_in)

    if not resposta:
        return {
            'ok': False
        }

    for linha in resposta.splitlines(False):
        if 'Subject:' in linha:
            try:

                match_cn = regex_cn.findall(linha)
                match_ou = regex_ou.findall(linha)
                match_o = regex_o.findall(linha)
                match_l = regex_l.findall(linha)
                match_st = regex_st.findall(linha)
                match_c = regex_c.findall(linha)
                match_email = regex_email.findall(linha)

                d.update({
                    'CN': match_cn[0][0] if match_cn else '',
                    'OU': match_ou[0][0] if match_ou else '',
                    'O': match_o[0][0] if match_o else '',
                    'L': match_l[0][0] if match_l else '',
                    'S': match_st[0][0] if match_st else '',
                    'C': match_c[0][0] if match_c else '',
                    'Email': match_email[0][0] if match_email else '',
                    'ok': True,
                })

            except:
                log.warning('Erro na decodificação da CSR (KeySize): %s\n' % csr)
                return {
                    'ok': False
                }

        elif 'Public-Key:' in linha:
            try:

                d['KeySize'] = int(re.findall('[0-9]+', linha)[0])

            except (IndexError, ValueError):
                log.warning('Erro na decodificação da CSR (KeySize): %s\n' % csr)
                return {
                    'ok': False
                }

        elif 'DNS' in linha:
            try:

                d['dnsNames'] = [s[4:] for s in map(str.strip, linha.split(','))]

            except:
                log.warning('Erro na decodificação da CSR (DNS): %s\n' % csr)
                return {
                    'ok': False
                }
        else:
            raise Exception('csr invalida')

    d['subject_ok'] = bool(d.get('CN') and d.get('O') and d.get('L') and d.get('S') and d.get('C'))

    return d


def decode_csr_comodo(csr, show_key_size=True, show_csr_hashes=True, show_san_dns=True):
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
                value = map(lambda x: x.strip(), value.split(',')) if value else []

            d[key.replace(' ', '')] = value

    d['subject_ok'] = d.get('CN') and d.get('O') and d.get('L') and d.get('S') and d.get('C')

    # Insere os dominios contidos na CSR que a comodo não retorna
    # Foi necessário pois a comodo possui um bug onde quando o CN vai em branco (caso do MDC),
    # ela não retorna nenhum dominio, mesmo que a CSR possua.

    dnsnames = d['dnsNames']

    path_in = cria_arquivo_temporario(csr)

    csr_data = run_command('openssl req -in %s -noout -text | grep DNS' % path_in)

    os.remove(path_in)

    for entry in csr_data.strip().split(','):
        if entry:
            dns = entry.strip().split(':')[1]
            if dns not in dnsnames:
                dnsnames.append(dns)

    return d


def compare_csr(csr_1, csr_2):
    if not csr_1['ok'] or not csr_2['ok']:
        return False
    if any(csr_1[f] != csr_2[f] for f in ('CN', 'OU', 'O', 'POBox', 'STREET1', 'STREET2', 'STREET3', 'L',
                                          'S', 'PostalCode', 'C', 'Email', 'Phone', 'KeySize')):
        return False
    if set(csr_1['dnsNames']) != set(csr_2['dnsNames']):
        return False
    return True


RAZOES_CACHE = {}


def get_razao_social_dominio(dominio):
    if dominio in RAZOES_CACHE:
        return RAZOES_CACHE[dominio]
    razao_social = commands.getoutput('whois %s | grep ^owner:' % dominio).strip()
    r = re.match('owner:\s*(.+)(\([0-9]+\))?', razao_social)
    if r:
        razao = r.groups()[0]
        RAZOES_CACHE[dominio] = razao
    else:
        razao = None
    return razao


EMAIL_CACHE = {}


def get_emails_dominio(dominio):
    if dominio in EMAIL_CACHE:
        return EMAIL_CACHE[dominio]

    resposta = commands.getoutput('whois %s | grep \'^\(Admin Email\|Tech Email\|e-mail\)\'' % dominio).splitlines()
    emails = []
    for email in resposta:
        r = re.match('(Admin Email|Tech Email|e-mail):\s*(.+)', email)
        if r:
            r = r.groups()[1]
            if r not in emails:
                emails.append(r)
    if emails:
        EMAIL_CACHE[dominio] = emails
    return emails


def remove_acentos(txt, codif='utf-8'):
    try:
        return normalize('NFKD', smart_unicode(txt)).encode('ASCII', 'ignore')
    except Exception:
        return normalize('NFKD', txt.decode('iso-8859-1')).encode('ASCII', 'ignore')


def comparacao_fuzzy(string1, string2, max_dist=10):
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