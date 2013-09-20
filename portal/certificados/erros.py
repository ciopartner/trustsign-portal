# coding=utf-8
from __future__ import unicode_literals


ERRO_INTERNO_SERVIDOR = -1
ERRO_CSR_INVALIDA_CN_NAO_PODE_CONTER_WILDCARD = -5
ERRO_CSR_INVALIDA_CN_PRECISA_DE_UNICO_WILDCARD = -6
ERRO_CSR_INVALIDA_FALTA_CAMPO_OBRIGATORIO = -8
ERRO_CSR_INVALIDO_TEXTO_BASE64_INVALIDO = -9
ERRO_CSR_INVALIDA_IMPOSSIVEL_DECODIFICAR = -10
ERRO_CSR_INVALIDA_ALGORITMO_NAO_SUPORTADO = -11
ERRO_CSR_INVALIDA_ASSINATURA_INVALIDA = -12
ERRO_CSR_INVALIDA_TAMANHO_CHAVE_INVALIDO = -13
ERRO_CSR_INVALIDA_CN_NAO_PODE_SER_NOME_DOMINIO = -18
ERRO_CSR_INVALIDA_CN_NAO_PODE_SER_UM_IP = -19
ERRO_CSR_INVALIDA_CHAVE_COMPROMETIDA = -40
ERRO_CERTIFICADO_REJEITADO = -20
ERRO_CERTIFICADO_REVOGADO = -21
ERRO_CERTIFICADO_EM_PROCESSO_EMISSAO = -26
ERRO_CERTIFICADO_JA_EXPIROU = -0
ERRO_CSR_INVALIDA_NAO_CONTEM_URL_DIGITADA = -100
ERRO_DADOS_CONTATO_TODOS_OS_DADOS_SAO_NECESSARIOS = -101
ERRO_DADOS_CONTATO_TELEFONE_PRECISA_SER_FIXO = -102
ERRO_CAMPO_DOMINIO_OBRIGATORIO = -103
ERRO_CAMPO_CSR_OBRIGATORIO = -104
ERRO_CSR_PRODUTO_EXIGE_CHAVE_2048_BITS = -105
ERRO_CSR_PRODUTO_EXIGE_CHAVE_4096_BITS = -106
ERRO_EMAIL_CONTATO_PRECISA_SER_DOMINIO = -107
ERRO_SITUACAO_CADASTRAL_INATIVA = -108
ERRO_CSR_ORGANIZATION_DIFERENTE_CNPJ = -109
ERRO_CSR_ENDERECO_DIFERENTE_CNPJ = -110
ERRO_DOMINIO_SEM_EMAIL_VALIDACAO = -111
ERRO_CAMPO_EMAIL_ENVIO_CERT_OBRIGATORIO = -112
ERRO_CAMPO_TIPO_SERVIDOR_OBRIGATORIO = -113
ERRO_VOUCHER_NAO_ENCONTRADO = -114
ERRO_SEM_CREDITO_FQDN = -115
ERRO_SEM_CREDITO_DOMINIO = -116
ERRO_CAMPO_CONTRATO_SOCIAL_OBRIGATORIO = -117
ERRO_CAMPO_COMPROV_END_OBRIGATORIO = -118
ERRO_CAMPO_COMPROV_TEL_OBRIGATORIO = -119
ERRO_CAMPO_CCSA_OBRIGATORIO = -120
ERRO_CAMPO_EVCR_OBRIGATORIO = -121
ERRO_FORMATO_ARQUIVOS_INVALIDOS = -122
ERRO_CSR_REEMISSAO_COM_CSR_DIFERENTE = -123
ERRO_CAMPO_MOTIVO_REVOGACAO_OBRIGATORIO = -124
ERRO_CAMPO_COMPROV_IDENT_OBRIGATORIO = -125
ERRO_CAMPO_SENHA_OBRIGATORIO = -126
ERRO_CAMPO_SENHA_NAO_SEGURA = -127


ERROS = {
    ERRO_INTERNO_SERVIDOR: 'Erro interno do servidor(%d)',
    ERRO_CSR_INVALIDA_CN_NAO_PODE_CONTER_WILDCARD: 'CSR Inválida: COMMON NAME não pode conter um wildcard (\'*\')',
    ERRO_CSR_INVALIDA_CN_PRECISA_DE_UNICO_WILDCARD: 'CSR Inválida: COMMON NAME precisa de um único wildcard (\'*\')',
    ERRO_CSR_INVALIDA_FALTA_CAMPO_OBRIGATORIO: 'Não foi possível ler a CSR: falta um campo obrigatório',
    ERRO_CSR_INVALIDO_TEXTO_BASE64_INVALIDO: 'Não foi possível ler a CSR: texto em base-64 inválido',
    ERRO_CSR_INVALIDA_IMPOSSIVEL_DECODIFICAR: 'Não foi possível ler a CSR: impossível decodificá-la',
    ERRO_CSR_INVALIDA_ALGORITMO_NAO_SUPORTADO: 'Não foi possível ler a CSR: algoritmo não suportado',
    ERRO_CSR_INVALIDA_ASSINATURA_INVALIDA: 'Não foi possível ler a CSR: assinatura inválida',
    ERRO_CSR_INVALIDA_TAMANHO_CHAVE_INVALIDO: 'Não foi possível ler a CSR: tamanho da chave inválido',
    ERRO_CSR_INVALIDA_CN_NAO_PODE_SER_NOME_DOMINIO: 'CSR Inválida: COMMON NAME não pode ser um nome de domínio',
    ERRO_CSR_INVALIDA_CN_NAO_PODE_SER_UM_IP: 'CSR Inválida: COMMON NAME não pode ser um IP(COMODO -19, -35,',
    ERRO_CSR_INVALIDA_CHAVE_COMPROMETIDA: 'CSR Inválida: está sendo utilizada uma chave que pode ter sido comprometida.'
                                          ' Sugere-se gerar nova chave e nova CSR.',
    ERRO_CERTIFICADO_REJEITADO: 'Este certificado já encontra-se rejeitado!',
    ERRO_CERTIFICADO_REVOGADO: 'Este certificado já encontra-se revogado!',
    ERRO_CERTIFICADO_EM_PROCESSO_EMISSAO: 'Este certificado está em processo de emissão!',
    ERRO_CERTIFICADO_JA_EXPIROU: 'Este certificado já expirou!',
    
    ERRO_CSR_INVALIDA_NAO_CONTEM_URL_DIGITADA: 'Esta CSR não contém a URL digitada',
    ERRO_DADOS_CONTATO_TODOS_OS_DADOS_SAO_NECESSARIOS: 'Dados de Contato: Todos os dados de contato são necessários',
    ERRO_DADOS_CONTATO_TELEFONE_PRECISA_SER_FIXO: 'Dados de Contato: O telefone precisa ser fixo e estar no formato (dd) 9999-9999',
    ERRO_CAMPO_DOMINIO_OBRIGATORIO: 'O campo de domínio é obrigatório',
    ERRO_CAMPO_CSR_OBRIGATORIO: 'O campo CSR é obrigatório',
    ERRO_CSR_PRODUTO_EXIGE_CHAVE_2048_BITS: 'Erro na CSR: para este produto o tamanho da chave obrigatoriamente deve ser 2048 bits',
    ERRO_CSR_PRODUTO_EXIGE_CHAVE_4096_BITS: 'Erro na CSR: para este produto o tamanho da chave obrigatoriamente deve ser 4096 bits',
    ERRO_EMAIL_CONTATO_PRECISA_SER_DOMINIO: 'O e-mail de contato obrigatoriamente precisa pertencer ao domínio do certificado a ser emitido (ou de um dos domínios no caso de certificado para múltiplos domínios)',
    ERRO_SITUACAO_CADASTRAL_INATIVA: 'A situação cadastral da empresa cliente não está ativa na Receita Federal do Brasil. Favor entrar em contato com o suporte.',
    ERRO_CSR_ORGANIZATION_DIFERENTE_CNPJ: 'É obrigatória a carta de cessão preenchida. Sugere-se que o campo ORGANIZATION da CSR seja idêntico ao do Cartão CNPJ para que este arquivo não seja obrigatório.',
    ERRO_CSR_ENDERECO_DIFERENTE_CNPJ: 'É obrigatória a carta de cessão preenchida. Sugere-se que os campos de endereço da CSR sejam idênticos ao do Cartão CNPJ para que este arquivo não seja obrigatório.',
    ERRO_DOMINIO_SEM_EMAIL_VALIDACAO: 'O(s) domínio(s) contido(s) na CSR precisa(m) estar com e-mail de validação do domínio preenchidos.',
    ERRO_CAMPO_EMAIL_ENVIO_CERT_OBRIGATORIO: 'É obrigatório informar um e-mail para envio da chave pública',
    ERRO_CAMPO_TIPO_SERVIDOR_OBRIGATORIO: 'É obrigatório informar o tipo de servidor que será instalado o certificado',
    ERRO_VOUCHER_NAO_ENCONTRADO: 'Voucher não encontrado. Contacte o suporte',
    ERRO_SEM_CREDITO_FQDN: 'Não há créditos suficientes de FQDN\'s adicionais para emitir este certificado. Considere adquirir FQDN\'s adicionais em nosso e-commerce.',
    ERRO_SEM_CREDITO_DOMINIO: 'Não há créditos suficientes de Domínios adicionais para emitir este certificado. Considere adquirir domínios adicionais em nosso e-commerce.',
    ERRO_CAMPO_CONTRATO_SOCIAL_OBRIGATORIO: 'É obrigatório o envio do Contrato Social',
    ERRO_CAMPO_COMPROV_END_OBRIGATORIO: 'É obrigatório o envio de Comprovante de Endereço',
    ERRO_CAMPO_COMPROV_TEL_OBRIGATORIO: 'É obrigatório o envio de Comprovante de Telefone',
    ERRO_CAMPO_CCSA_OBRIGATORIO: 'É obrigatório o envio do “Comodo Certificate Subscriber Agreement”',
    ERRO_CAMPO_EVCR_OBRIGATORIO: 'É obrigatório o envio do “Termo de Solicitação de EV (EV Certifcate Request)”',
    ERRO_FORMATO_ARQUIVOS_INVALIDOS: 'É obrigatório o envio de arquivo em extensão PDF ou ZIP',
    ERRO_CSR_REEMISSAO_COM_CSR_DIFERENTE: 'Na reemissão de um certificado é necessário que todos os campos da nova CSR sejam idênticos a CSR do certificado antigo',
    ERRO_CAMPO_MOTIVO_REVOGACAO_OBRIGATORIO: 'É obrigatório fornecer um motivo para a revogação do certificado',
    ERRO_CAMPO_COMPROV_IDENT_OBRIGATORIO: 'É obrigatório o envio de documento de identificação com foto',
    ERRO_CAMPO_SENHA_OBRIGATORIO: 'É obrigatório o preenchimento de uma senha para este certificado',
    ERRO_CAMPO_SENHA_NAO_SEGURA: 'Esta senha não é considerada segura, favor tentar outra senha',
}


class APIError(Exception):
    code = None
    message = None

    def __init__(self, code, message=None, *args, **kwargs):
        super(APIError, self).__init__(message=message, *args, **kwargs)
        self.code = code
        if not message:
            self.message = ERROS.get(code, ERROS.get(ERRO_INTERNO_SERVIDOR) % '0')