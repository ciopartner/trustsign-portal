from portal.certificados.models import Emissao
from portal.certificados.validations import EmissaoModelSerializer, ValidateEmissaoUrlMixin, ValidateEmissaoCSRMixin, \
    ValidateEmissaoValidacaoEmail, ValidateEmissaoPrimaryDN, ValidateEmissaoComprovanteEndereco, \
    ValidateEmissaoContratoSocial, ValidateEmissaoCCSA, ValidateEmissaoEVCR


class EmissaoNv0Serializer(EmissaoModelSerializer, ValidateEmissaoUrlMixin):
    REQUIRED_FIELDS = ('emissao_url', )

    class Meta:
        model = Emissao
        fields = ('crm_hash', 'emissao_url', 'emissao_carta')


class EmissaoNv1Serializer(EmissaoModelSerializer, ValidateEmissaoUrlMixin, ValidateEmissaoCSRMixin,
                           ValidateEmissaoValidacaoEmail):
    REQUIRED_FIELDS = ('emissao_url', 'emissao_validacao_email', 'emissao_certificado_envio_email',
                       'emissao_servidor_tipo', 'emissao_csr')

    class Meta:
        model = Emissao
        fields = ('crm_hash', 'emissao_url', 'emissao_validacao_email', 'emissao_certificado_envio_email',
                  'emissao_servidor_tipo', 'emissao_csr', 'emissao_carta')


class EmissaoNv2Serializer(EmissaoModelSerializer, ValidateEmissaoUrlMixin, ValidateEmissaoCSRMixin,
                           ValidateEmissaoPrimaryDN):
    REQUIRED_FIELDS = ('emissao_url', 'emissao_validacao_email', 'emissao_certificado_envio_email',
                       'emissao_servidor_tipo', 'emissao_csr', 'emissao_primary_dn', )

    class Meta:
        model = Emissao
        fields = ('crm_hash', 'emissao_url', 'emissao_csr', 'emissao_primary_dn', 'emissao_validacao_email',
                  'emissao_certificado_envio_email', 'emissao_servidor_tipo', 'emissao_carta')


class EmissaoNv3Serializer(EmissaoModelSerializer, ValidateEmissaoUrlMixin, ValidateEmissaoCSRMixin,
                           ValidateEmissaoContratoSocial, ValidateEmissaoComprovanteEndereco,
                           ValidateEmissaoEVCR, ValidateEmissaoCCSA):
    validacao_manual = True

    REQUIRED_FIELDS = ('emissao_url', 'emissao_validacao_email', 'emissao_certificado_envio_email',
                       'emissao_servidor_tipo', 'emissao_csr', 'emissao_contrato_social',
                       'emissao_comprovante_endereco', 'emissao_ccsa', 'emissao_evcr')

    class Meta:
        model = Emissao
        fields = ('crm_hash', 'emissao_url', 'emissao_certificado_envio_email', 'emissao_validacao_email',
                  'emissao_servidor_tipo', 'emissao_csr', 'emissao_carta', 'emissao_contrato_social',
                  'emissao_comprovante_endereco', 'emissao_ccsa', 'emissao_evcr')


class EmissaoNv4Serializer(EmissaoModelSerializer, ValidateEmissaoCSRMixin, ValidateEmissaoPrimaryDN,
                           ValidateEmissaoContratoSocial, ValidateEmissaoComprovanteEndereco,
                           ValidateEmissaoEVCR, ValidateEmissaoCCSA):
    REQUIRED_FIELDS = ('emissao_url', 'emissao_validacao_email', 'emissao_certificado_envio_email',
                       'emissao_servidor_tipo', 'emissao_csr', 'emissao_contrato_social',
                       'emissao_comprovante_endereco', 'emissao_ccsa', 'emissao_evcr', 'emissao_primary_dn')

    class Meta:
        model = Emissao
        fields = ('crm_hash', 'emissao_url', 'emissao_fqdns', 'emissao_certificado_envio_email',
                  'emissao_validacao_email', 'emissao_servidor_tipo', 'emissao_csr', 'emissao_primary_dn',
                  'emissao_carta', 'emissao_contrato_social', 'emissao_comprovante_endereco', 'emissao_ccsa',
                  'emissao_evcr')


class EmissaoNvASerializer(EmissaoModelSerializer, ValidateEmissaoComprovanteEndereco):
    REQUIRED_FIELDS = ('emissao_comprovante_endereco',)

    class Meta:
        model = Emissao
        fields = ('crm_hash', 'emissao_comprovante_endereco',)