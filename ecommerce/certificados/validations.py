# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from ecommerce.certificados import erros as e
from libs.comodo import get_emails_validacao_padrao, get_emails_validacao
from ecommerce.certificados.erros import get_erro_message
from ecommerce.certificados.models import Voucher
from portal.suporte.utils import comparacao_fuzzy, get_razao_social_dominio

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
                raise self.ValidationError(get_erro_message(e.ERRO_DOMINIO_SEM_WILDCARD))
        else:
            if '*' in valor:
                raise self.ValidationError(get_erro_message(e.ERRO_DOMINIO_COM_WILDCARD))
        
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
        try:
            voucher = self.get_voucher()
        except Voucher.DoesNotExist:
            raise self.ValidationError(get_erro_message(e.ERRO_VOUCHER_NAO_EXISTENTE))

        if voucher.ssl_product == Voucher.PRODUTO_SMIME:
            return valor

        csr = self.get_csr_decoded(valor)
        url = fields.get('emission_url', '')

        if not csr['ok']:
            raise self.ValidationError(get_erro_message(e.ERRO_CSR_INVALIDA_IMPOSSIVEL_DECODIFICAR))

        if csr.get('CN') != url and voucher.ssl_product not in (Voucher.PRODUTO_MDC, Voucher.PRODUTO_EV_MDC,
                                                                Voucher.PRODUTO_CODE_SIGNING, Voucher.PRODUTO_JRE):
            raise self.ValidationError(get_erro_message(e.ERRO_CSR_INVALIDA_CN_DEVE_CONTER_DOMINIO))

        # if not comparacao_fuzzy(csr.get('O'), voucher.customer_companyname):
        #     raise self.ValidationError(get_erro_message(e.ERRO_CSR_ORGANIZATION_DIFERENTE_CNPJ))

        key_size = int(csr.get('KeySize'))
        if voucher.ssl_product in (Voucher.PRODUTO_SMIME, Voucher.PRODUTO_CODE_SIGNING, Voucher.PRODUTO_JRE):
            if key_size != 2048:
                raise self.ValidationError(get_erro_message(e.ERRO_CSR_PRODUTO_EXIGE_CHAVE_2048_BITS))
        else:
            if voucher.ssl_line in (voucher.LINHA_BASIC, voucher.LINHA_PRO) and key_size != 2048:
                raise self.ValidationError(get_erro_message(e.ERRO_CSR_PRODUTO_EXIGE_CHAVE_2048_BITS))

            if voucher.ssl_line == voucher.LINHA_PRIME and key_size != 4096:
                raise self.ValidationError(get_erro_message(e.ERRO_CSR_PRODUTO_EXIGE_CHAVE_4096_BITS))

        dominios = fields.get('emission_urls')

        if dominios:
            dominios = dominios.split(' ')
        else:
            dominios = csr.get('dnsNames', [])

        if voucher.ssl_product not in (Voucher.PRODUTO_MDC, Voucher.PRODUTO_SAN_UCC, Voucher.PRODUTO_EV_MDC):
            if dominios:
                raise self.ValidationError(get_erro_message(e.ERRO_CSR_INVALIDA_DNS_PREECHIDO))

            if voucher.ssl_product in (Voucher.PRODUTO_CODE_SIGNING, Voucher.PRODUTO_JRE) and \
                    comparacao_fuzzy(csr.get('CN'), voucher.customer_companyname):
                if fields.get('emission_assignment_letter'):
                    self.validacao_manual = True
                else:
                    if self.validacao:
                        self.validacao_carta_cessao_necessaria = True
        else:
            if voucher.ssl_product == Voucher.PRODUTO_SAN_UCC:
                produto_adicional = Voucher.PRODUTO_SSL_SAN_FQDN
            elif voucher.ssl_product == Voucher.PRODUTO_MDC:
                produto_adicional = Voucher.PRODUTO_SSL_MDC_DOMINIO
            else:
                produto_adicional = Voucher.PRODUTO_SSL_EV_MDC_DOMINIO

            qtd_dominios_disponiveis = 5 + Voucher.objects.filter(
                ssl_product=produto_adicional,
                emissao__isnull=True,
                ssl_line=voucher.ssl_line,
                ssl_term=voucher.ssl_term
            ).count()

            if len(dominios) > qtd_dominios_disponiveis:
                if voucher.ssl_product == voucher.PRODUTO_SAN_UCC:
                    raise self.ValidationError(get_erro_message(e.ERRO_SEM_CREDITO_FQDN))
                raise self.ValidationError(get_erro_message(e.ERRO_SEM_CREDITO_DOMINIO))

            for dominio in dominios:
                if '*' in dominio:
                    raise self.ValidationError(get_erro_message(e.ERRO_DOMINIO_COM_WILDCARD))

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
        return valor


@insere_metodos_validacao('emission_dcv_emails')
class ValidateEmissaoValidacaoEmail(object):

    def _valida_emission_dcv_emails(self, valor, fields):
        emails = get_emails_validacao(fields['emission_url'])
        if valor not in emails:
            raise self.ValidationError(get_erro_message(e.ERRO_EMAIL_VALIDACAO_INVALIDO))
        return valor

@insere_metodos_validacao('emission_dcv_emails')
class ValidateEmissaoValidacaoEmailMultiplo(object):

    def _valida_emission_dcv_emails(self, valor, fields):
        voucher = self.get_voucher()

        dominios = fields.get('emission_urls')

        if dominios:
            dominios = dominios.split(' ')
        else:
            csr = self.get_csr_decoded(valor)
            dominios = csr.get('dnsNames', [])

        emails = valor.split(' ')

        if len(dominios) != len(emails):
            raise self.ValidationError(get_erro_message(e.ERRO_DOMINIO_SEM_EMAIL_VALIDACAO))

        for dominio, email in zip(dominios, emails):
            final_dominio = '.%s' % dominio.split('.')[-1]
            if self.get_voucher().ssl_product == Voucher.PRODUTO_SAN_UCC and final_dominio in NOMES_INTERNOS:
                continue

            if email not in get_emails_validacao_padrao(dominio):
                raise self.ValidationError(get_erro_message(e.ERRO_EMAIL_VALIDACAO_INVALIDO_PARA_DOMINIO) % (email, dominio))
        return valor


class ValidateFormatoArquivos(object):

    def _valida_arquivo(self, arquivo):
        if arquivo and arquivo.name[-4:].lower() not in ('.pdf', '.zip'):
            raise self.ValidationError(get_erro_message(e.ERRO_FORMATO_ARQUIVOS_INVALIDOS))
        return arquivo


@insere_metodos_validacao('emission_assignment_letter')
class ValidateEmissaoAssignmentLetter(ValidateFormatoArquivos):

    def _valida_emission_assignment_letter(self, valor, fields):
        return self._valida_arquivo(valor)


@insere_metodos_validacao('emission_articles_of_incorporation')
class ValidateEmissaoArticlesOfIncorporation(ValidateFormatoArquivos):

    def _valida_emission_articles_of_incorporation(self, valor, fields):
        return self._valida_arquivo(valor)


@insere_metodos_validacao('emission_address_proof')
class ValidateEmissaoAddressProof(ValidateFormatoArquivos):

    def _valida_emission_address_proof(self, valor, fields):
        return self._valida_arquivo(valor)


@insere_metodos_validacao('emission_ccsa')
class ValidateEmissaoCCSA(ValidateFormatoArquivos):

    def _valida_emission_ccsa(self, valor, fields):
        return self._valida_arquivo(valor)


@insere_metodos_validacao('emission_evcr')
class ValidateEmissaoEVCR(ValidateFormatoArquivos):

    def _valida_emission_evcr(self, valor, fields):
        return self._valida_arquivo(valor)


@insere_metodos_validacao('emission_phone_proof')
class ValidateEmissaoPhoneProof(ValidateFormatoArquivos):

    def _valida_emission_phone_proof(self, valor, fields):
        return self._valida_arquivo(valor)


@insere_metodos_validacao('emission_id')
class ValidateEmissaoID(ValidateFormatoArquivos):

    def _valida_emission_id(self, valor, fields):
        return self._valida_arquivo(valor)