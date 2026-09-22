"""Regras de calculo automatico de status/vencimento dos contratos.

Mantidas separadas do restante do codigo para que os limites (30/15/7 dias)
possam se tornar configuraveis por empresa no futuro sem tocar nos routers.
"""
from datetime import date
from app.config import settings
from app import models


def dias_para_vencer(data_fim: date, hoje: date | None = None) -> int:
    hoje = hoje or date.today()
    return (data_fim - hoje).days


def calcular_status_automatico(contract: models.Contract, hoje: date | None = None) -> models.ContractStatus:
    """So recalcula automaticamente quando o contrato esta num estado 'passivo'
    (vigente / proximo_vencimento / vencido). Estados de fluxo de renovacao ou
    ja finalizados (em_renovacao, aguardando_assinatura_*, renovado, cancelado)
    nao sao sobrescritos por esta rotina.
    """
    estados_controlados_pelo_fluxo = {
        models.ContractStatus.em_renovacao,
        models.ContractStatus.aguardando_assinatura_cliente,
        models.ContractStatus.aguardando_assinatura_empresa,
        models.ContractStatus.renovado,
        models.ContractStatus.cancelado,
    }
    if contract.status in estados_controlados_pelo_fluxo:
        return contract.status

    restante = dias_para_vencer(contract.data_fim, hoje)
    if restante < 0:
        return models.ContractStatus.vencido
    if restante <= settings.DIAS_ALERTA_VENCIMENTO:
        return models.ContractStatus.proximo_vencimento
    return models.ContractStatus.vigente


def mensagem_vencimento(restante: int) -> str | None:
    if restante == 30:
        return "Seu contrato esta proximo do vencimento. Vence em 30 dias."
    if restante == 15:
        return "Seu contrato vence em 15 dias."
    if restante == 7:
        return "Seu contrato vence em 7 dias."
    if restante == 0:
        return "Seu contrato vence hoje."
    if restante == -1:
        return "Seu contrato venceu."
    return None
