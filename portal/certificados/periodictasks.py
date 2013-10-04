# coding=utf-8
from __future__ import unicode_literals
from django.conf import settings
from periodically.decorators import every
from portal.certificados import comodo
from portal.certificados.models import Emissao, Revogacao
from logging import getLogger

log = getLogger('portal.certificados.periodictasks')

@every(minutes=5)
def envia_comodo():
    status_envio_pendente = (
        Emissao.STATUS_EMISSAO_ENVIO_COMODO_PENDENTE,
        Emissao.STATUS_REEMISSAO_ENVIO_COMODO_PENDENTE,
        Emissao.STATUS_REVOGACAO_ENVIO_COMODO_PENDENTE,
    )

    for emissao in Emissao.objects.select_related('voucher', 'revogacao').filter(emission_status=status_envio_pendente):
        try:
            if emissao.emission_status == Emissao.STATUS_EMISSAO_ENVIO_COMODO_PENDENTE:
                voucher = emissao.voucher
                # TODO: retirar if após implementar api comodo para os outros produtos
                if voucher.ssl_product not in (voucher.PRODUTO_SMIME, voucher.PRODUTO_CODE_SIGNING, voucher.PRODUTO_JRE):
                    resposta = comodo.emite_certificado(emissao)

                    emissao.comodo_order = resposta['orderNumber']
                    emissao.emission_cost = resposta['totalCost']
                    emissao.emission_status = Emissao.STATUS_EMISSAO_ENVIADO_COMODO

            elif emissao.emission_status == Emissao.STATUS_REEMISSAO_ENVIO_COMODO_PENDENTE:
                # Como o ambiente de testes não existe para reemissão...
                if not settings.COMODO_ENVIAR_COMO_TESTE:
                    comodo.reemite_certificado(emissao)
                    emissao.emission_status = emissao.STATUS_REEMISSAO_ENVIADO_COMODO
            else:
                try:
                    comodo.revoga_certificado(emissao.revogacao)
                    emissao.status = Emissao.STATUS_REVOGACAO_ENVIADO_COMODO

                except Revogacao.DoesNotExist:
                    log.error('Tentando revogar uma emissão sem criar a revogação no banco')

        except comodo.ComodoError as e:
            log.error('Ocorreu um erro(%s) na chamada da comodo da emissao: %s' % (e.code, emissao))

            emissao.emission_status = Emissao.OCORREU_ERRO_COMODO
            emissao.emission_error_message = '%s (%s)' % (e.comodo_message, e.code)

        emissao.save()