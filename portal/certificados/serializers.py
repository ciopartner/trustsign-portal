from portal.certificados.models import Emissao
from portal.certificados.validations import CustomModelSerializer, ValidateEmissaoUrlMixin, ValidateEmissaoCSRMixin


class EmissaoNv0Serializer(CustomModelSerializer, ValidateEmissaoUrlMixin):
    FIELDS_REQUIRED = ('emissao_url', )

    class Meta:
        model = Emissao
        fields = ('crm_hash', 'emissao_url', 'emissao_carta')


class EmissaoNv1Serializer(CustomModelSerializer, ValidateEmissaoUrlMixin, ValidateEmissaoCSRMixin):
    REQUIRED_FIELDS = ('emissao_url', 'emissao_validacao_email', 'emissao_certificado_envio_email',
                       'emissao_servidor_tipo', 'emissao_csr')

    class Meta:
        model = Emissao
        fields = ('crm_hash', 'emissao_url', 'emissao_validacao_email', 'emissao_certificado_envio_email',
                  'emissao_servidor_tipo', 'emissao_csr', 'emissao_carta')


class EmissaoNv2Serializer(CustomModelSerializer):
    REQUIRED_FIELDS = ('emissao_url', 'emissao_validacao_email', 'emissao_certificado_envio_email',
                       'emissao_servidor_tipo', 'emissao_csr', 'emissao_primary_dn', )

    class Meta:
        model = Emissao
        fields = ('crm_hash', 'emissao_url', 'emissao_csr', 'emissao_primary_dn', 'emissao_validacao_email',
                  'emissao_certificado_envio_email', 'emissao_servidor_tipo', 'emissao_carta')


class EmissaoNv3Serializer(CustomModelSerializer):
    REQUIRED_FIELDS = ('emissao_url', 'emissao_validacao_email', 'emissao_certificado_envio_email',
                       'emissao_servidor_tipo', 'emissao_csr', 'emissao_contrato_social',
                       'emissao_comprovante_endereco', 'emissao_ccsa', 'emissao_evcr')

    class Meta:
        model = Emissao
        fields = ('crm_hash', 'emissao_url', 'emissao_certificado_envio_email', 'emissao_validacao_email',
                  'emissao_servidor_tipo', 'emissao_csr', 'emissao_carta', 'emissao_contrato_social',
                  'emissao_comprovante_endereco', 'emissao_ccsa', 'emissao_evcr')


class EmissaoNv4Serializer(CustomModelSerializer):
    REQUIRED_FIELDS = ('emissao_url', 'emissao_validacao_email', 'emissao_certificado_envio_email',
                       'emissao_servidor_tipo', 'emissao_csr', 'emissao_contrato_social',
                       'emissao_comprovante_endereco', 'emissao_ccsa', 'emissao_evcr', 'emissao_primary_dn',
                       'emissao_fqdns')

    class Meta:
        model = Emissao
        fields = ('crm_hash', 'emissao_url', 'emissao_fqdns', 'emissao_certificado_envio_email',
                  'emissao_validacao_email', 'emissao_servidor_tipo', 'emissao_csr', 'emissao_primary_dn',
                  'emissao_carta', 'emissao_contrato_social', 'emissao_comprovante_endereco', 'emissao_ccsa',
                  'emissao_evcr')


class EmissaoNvASerializer(CustomModelSerializer):
    REQUIRED_FIELDS = ('emissao_comprovante_endereco',)

    class Meta:
        model = Emissao
        fields = ('crm_hash', 'emissao_comprovante_endereco',)