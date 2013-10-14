# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from libs.comodo import get_emails_validacao_padrao, get_emails_validacao
from portal.certificados.erros import get_erro_message
from portal.certificados.models import Voucher
from portal.ferramentas.utils import comparacao_fuzzy, get_razao_social_dominio
from portal.certificados import erros as e

NOMES_INTERNOS = (
    '.test',
    '.example',
    '.invalid',
    '.localhost',
    '.local',
    '.lan',
    '.priv',
    '.localdomain',
)


def insere_metodos_validacao(field):
    """
    Decorator que cria os métodos clean_FIELD e validate_FIELD usados pelo
    form do django e pelo serializer do djangorestframework respectivamente,
    que por sua vez chama o método _valida_FIELD onde deve ser conter a validação

    Exemplo:
        @insere_metodos_validacao('campo')
        class ValidateCampoMixin(object):
            def _valida_campo(self, valor):
                ...
                return valor
    """
    def wrap(klass):
        def validade_rest(self, attrs, source):
            funcao_valida_campo = getattr(self, '_valida_%s' % field)
            attrs[source] = funcao_valida_campo(attrs.get(source, ''), attrs)
            return attrs

        def clean_django(self):
            funcao_valida_campo = getattr(self, '_valida_%s' % field)
            return funcao_valida_campo(self.cleaned_data[field], self.cleaned_data)

        setattr(klass, 'clean_%s' % field, clean_django)
        setattr(klass, 'validate_%s' % field, validade_rest)

        return klass
    return wrap


@insere_metodos_validacao('emission_url')
class ValidateEmissaoUrlMixin(object):

    def _valida_emission_url(self, valor, fields):
        try:
            voucher = self.get_voucher()
        except Voucher.DoesNotExist:
            raise self.ValidationError(get_erro_message(e.ERRO_VOUCHER_NAO_ENCONTRADO))
        
        if voucher.ssl_product in (Voucher.PRODUTO_MDC, Voucher.PRODUTO_EV_MDC, Voucher.PRODUTO_CODE_SIGNING,
                                   Voucher.PRODUTO_JRE, Voucher.PRODUTO_SMIME):
            return valor  # MDC, CS, JRE, SMIME não usa a emission_url
        
        if voucher.ssl_product == Voucher.PRODUTO_SSL_WILDCARD:
            if not valor.startswith('*.'):
                raise self.ValidationError('A URL deve iniciar com "*.". Ex.: *.exemplo.com.br')
        else:
            if '*' in valor:
                raise self.ValidationError('A URL não pode conter *.')
        
        razao_social = get_razao_social_dominio(valor)
        if not razao_social or not comparacao_fuzzy(razao_social, voucher.customer_companyname):
            if fields.get('emission_assignment_letter'):
                # se a razão social for diferente, mas o cliente enviar uma carta de cessão,
                # será preciso validação manual
                self.validacao_manual = True

            else:
                if self.validacao:
                    self.validacao_carta_cessao_necessaria = True
        return valor


@insere_metodos_validacao('emission_csr')
class ValidateEmissaoCSRMixin(object):

    def _valida_emission_csr(self, valor, fields):
        csr = self.get_csr_decoded(valor)
        url = fields.get('emission_url', '')

        if not csr['ok']:
            raise self.ValidationError('CSR Inválida')

        try:
            voucher = self.get_voucher()
        except Voucher.DoesNotExist:
            raise self.ValidationError()

        if csr.get('CN') != url and voucher.ssl_product not in (Voucher.PRODUTO_MDC, Voucher.PRODUTO_EV_MDC,
                                                                Voucher.PRODUTO_CODE_SIGNING, Voucher.PRODUTO_JRE):
            raise self.ValidationError('O campo Common Name(CN) deve conter o domínio escolhido')

        # if not comparacao_fuzzy(csr.get('O'), voucher.customer_companyname):
        #     raise self.ValidationError(get_erro_message(e.ERRO_CSR_ORGANIZATION_DIFERENTE_CNPJ))

        key_size = int(csr.get('KeySize'))
        if voucher.ssl_line in (voucher.LINHA_BASIC, voucher.LINHA_PRO) and key_size != 2048:
            raise self.ValidationError(get_erro_message(e.ERRO_CSR_PRODUTO_EXIGE_CHAVE_2048_BITS))

        if voucher.ssl_line == voucher.LINHA_PRIME and key_size != 4096:
            raise self.ValidationError(get_erro_message(e.ERRO_CSR_PRODUTO_EXIGE_CHAVE_4096_BITS))

        dominios = csr.get('dnsNames', [])
        if voucher.ssl_product not in (Voucher.PRODUTO_MDC, Voucher.PRODUTO_SAN_UCC, Voucher.PRODUTO_EV_MDC):
            if dominios:
                raise self.ValidationError('Este produto possui somente um domínio')

            if voucher.ssl_product in (Voucher.PRODUTO_CODE_SIGNING, Voucher.PRODUTO_JRE) and \
                    comparacao_fuzzy(csr.get('CN'), voucher.customer_companyname):
                if fields.get('emission_assignment_letter'):
                    self.validacao_manual = True
                else:
                    if self.validacao:
                        self.validacao_carta_cessao_necessaria = True
        else:

            #if len(dominios) > voucher.ssl_domains_qty:
            #    if voucher.ssl_product == voucher.PRODUTO_SAN_UCC:
            #        raise self.ValidationError(get_erro_message(e.ERRO_SEM_CREDITO_FQDN))
            #    raise self.ValidationError(get_erro_message(e.ERRO_SEM_CREDITO_DOMINIO))

            for dominio in dominios:
                if '*' in dominio:
                    raise self.ValidationError('Nenhum domínio pode conter *.')

                final_dominio = '.%s' % dominio.split('.')[-1]
                if voucher.ssl_product == Voucher.PRODUTO_SAN_UCC and final_dominio in NOMES_INTERNOS:
                    continue

                razao_social = get_razao_social_dominio(dominio)
                if not razao_social or not comparacao_fuzzy(razao_social, voucher.customer_companyname):
                    if fields.get('emission_assignment_letter'):
                        self.validacao_manual = True
                    else:
                        if self.validacao:
                            self.validacao_carta_cessao_necessaria = True
            #TODO: TBD > Chamar o serviço da COMODO para validar o e-mail de confirmação enviado pela API
        return valor


@insere_metodos_validacao('emission_primary_dn')
class ValidateEmissaoPrimaryDN(object):

    def _valida_emission_primary_dn(self, valor, fields):
        csr = self.get_csr_decoded(fields['emission_csr'])
        if not valor.strip() in csr.get('dnsNames'):
            raise self.ValidationError('O domínio primário não consta na lista de domínios na CSR')
        return valor


@insere_metodos_validacao('emission_dcv_emails')
class ValidateEmissaoValidacaoEmail(object):

    def _valida_emission_dcv_emails(self, valor, fields):
        emails = get_emails_validacao(fields['emission_url'])
        if valor not in emails:
            raise self.ValidationError('E-mail de validação inválido')
        return valor

@insere_metodos_validacao('emission_dcv_emails')
class ValidateEmissaoValidacaoEmailMultiplo(object):

    def _valida_emission_dcv_emails(self, valor, fields):
        voucher = self.get_voucher()
        csr = self.get_csr_decoded(valor)

        dominios = csr['dnsNames']
        emails = valor.split(' ')
        url = fields['emission_url']

        if voucher.ssl_product == Voucher.PRODUTO_SAN_UCC and url not in dominios:
            dominios.insert(0, url)

        if len(dominios) != len(emails):
            raise self.ValidationError(get_erro_message(e.ERRO_DOMINIO_SEM_EMAIL_VALIDACAO))

        for dominio, email in zip(dominios, emails):
            final_dominio = '.%s' % dominio.split('.')[-1]
            if self.get_voucher().ssl_product == Voucher.PRODUTO_SAN_UCC and final_dominio in NOMES_INTERNOS:
                continue

            if email not in get_emails_validacao_padrao(dominio):
                raise self.ValidationError('E-mail de validação inválido: %s para o domínio %s' % (email, dominio))
        return valor