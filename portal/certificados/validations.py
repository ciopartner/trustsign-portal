# coding=utf-8
from __future__ import unicode_literals
from portal.certificados.comodo import get_emails_validacao_padrao
from portal.certificados.models import Voucher
from portal.ferramentas.utils import comparacao_fuzzy, get_razao_social_dominio


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
            attrs[source] = funcao_valida_campo(attrs[source], attrs)
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
        razao_social = get_razao_social_dominio(valor)
        if not razao_social:
            raise self.ValidationError('Não foi possível conseguir a razão social apartir da url informada')

        try:
            voucher = self.get_voucher()
        except Voucher.DoesNotExist:
            raise self.ValidationError('Voucher não encontrado')

        if not comparacao_fuzzy(razao_social, voucher.customer_companyname):
            if fields.get('emission_assignment_letter'):
                # se a razão social for diferente, mas o cliente enviar uma carta de cessão,
                # será preciso validação manual
                self.validacao_manual = True

            else:
                raise self.ValidationError('A entidade no registro.br não é a mesma da razão social do CNPJ.')
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
            raise self.ValidationError('Voucher não encontrado')

        if csr.get('CN') != url:
            raise self.ValidationError('O campo Common Name(CN) deve conter o domínio escolhido')

        if not comparacao_fuzzy(csr.get('O'), voucher.customer_companyname):
            raise self.ValidationError('O campo Organization Name (O) deve conter a razão social: %s' % voucher.customer_companyname)

        key_size = int(csr.get('KeySize'))
        if voucher.ssl_line in (voucher.LINHA_BASIC, voucher.LINHA_PRO) and key_size != 2048:
            raise self.ValidationError('O tamanho da chave para produtos das linhas Basic e Pro deve ser 2048')

        if voucher.ssl_line == voucher.LINHA_PRIME and key_size != 4096:
            raise self.ValidationError('O tamanho da chave para produtos da linha Prime deve ser 4096')

        if voucher.ssl_product in (voucher.PRODUTO_MDC, voucher.PRODUTO_SAN_UCC, voucher.PRODUTO_EV_MDC):
            dominios = csr.get('dnsNames', [])
            if len(dominios) > voucher.ssl_domains_qty:
                raise self.ValidationError('A CSR possui mais domínios que a quantidade comprada: %s' % voucher.ssl_domains_qty)
            for dominio in dominios:
                if dominio.startswith('*.'):
                    dominio = dominio[2:]
                razao_social = get_razao_social_dominio(dominio)
                if not razao_social:
                    raise self.ValidationError('Não foi possível conseguir a razão social apartir do domínio: %s' % dominio)
                if not comparacao_fuzzy(razao_social, voucher.customer_companyname):
                    if fields.get('emission_assignment_letter'):
                        self.validacao_manual = True
                    else:
                        raise self.ValidationError('A razão social do seu CNPJ não bate com a do domínio: %s' % dominio)
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
        emails = get_emails_validacao_padrao(fields['emission_url'])
        if valor not in emails:
            raise self.ValidationError('E-mail de validação inválido')
        return valor

@insere_metodos_validacao('emission_dcv_emails')
class ValidateEmissaoValidacaoEmailMultiplo(object):

    def _valida_emission_dcv_emails(self, valor, fields):
        dominios = fields['emission_fqdns'].split(' ')
        emails = valor.split(' ')

        if len(dominios) != len(emails):
            raise self.ValidationError('Número de e-mails diferente do número de domínios')

        for dominio, email in zip(dominios, emails):
            if email not in get_emails_validacao_padrao(dominio):
                raise self.ValidationError('E-mail de validação inválido: %s para o domínio %s' % (email, dominio))
        return valor