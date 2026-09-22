import json
from datetime import datetime, date

from sqlalchemy.orm import Session

from app import models
from app.services.notify import notify


def _parse_dados(renewal: models.Renewal) -> dict:
    return json.loads(renewal.dados_json) if renewal.dados_json else {}


def merge_dados(renewal: models.Renewal, novos: dict, etapa: str | None = None) -> dict:
    atual = _parse_dados(renewal)
    if etapa:
        atual[etapa] = novos
    else:
        atual.update({k: v for k, v in novos.items() if v is not None})
    renewal.dados_json = json.dumps(atual, default=str)
    return atual


def finalizar_renovacao(db: Session, renewal: models.Renewal) -> models.Contract:
    """Chamado apos as assinaturas (cliente + empresa) terem sido registradas.

    Cria um NOVO registro de contrato (o antigo nunca e sobrescrito - regra
    #1 do projeto), marca o antigo como 'renovado' e conclui a renovacao.
    """
    contrato_antigo = renewal.contract
    dados = _parse_dados(renewal)

    if renewal.tipo == models.RenewalType.aditivo:
        novo_valor = dados.get("novo_valor") or float(contrato_antigo.valor)
        nova_inicio = dados.get("nova_data_inicio") or contrato_antigo.data_fim.isoformat()
        nova_fim = dados.get("nova_data_fim")
        condicoes = contrato_antigo.condicoes
        numero_sufixo = "-ADT"
    else:
        contratuais = dados.get("contratuais", {})
        novo_valor = contratuais.get("valor") or float(contrato_antigo.valor)
        nova_inicio = contratuais.get("data_inicio") or contrato_antigo.data_fim.isoformat()
        nova_fim = contratuais.get("data_fim")
        condicoes = contratuais.get("condicoes") or contrato_antigo.condicoes
        numero_sufixo = "-REN"

    if not nova_fim:
        # fallback de seguranca: soma 1 ano a data de inicio
        ini = date.fromisoformat(nova_inicio) if isinstance(nova_inicio, str) else nova_inicio
        nova_fim = date(ini.year + 1, ini.month, ini.day).isoformat()

    ano = datetime.utcnow().year
    novo_numero = f"{contrato_antigo.numero.split('-')[0]}{numero_sufixo}-{ano}"

    novo_contrato = models.Contract(
        numero=novo_numero,
        client_id=contrato_antigo.client_id,
        patient_id=contrato_antigo.patient_id,
        tipo=contrato_antigo.tipo,
        status=models.ContractStatus.vigente,
        valor=novo_valor,
        data_inicio=nova_inicio if isinstance(nova_inicio, date) else date.fromisoformat(nova_inicio),
        data_fim=nova_fim if isinstance(nova_fim, date) else date.fromisoformat(nova_fim),
        condicoes=condicoes,
        tipo_proxima_renovacao=contrato_antigo.tipo_proxima_renovacao,
        contrato_anterior_id=contrato_antigo.id,
    )
    db.add(novo_contrato)

    contrato_antigo.status = models.ContractStatus.renovado

    renewal.status = models.RenewalStatus.concluida
    renewal.completed_at = datetime.utcnow()

    db.flush()
    renewal.novo_contract_id = novo_contrato.id
    db.commit()
    db.refresh(novo_contrato)

    notify(db, contrato_antigo.client_id, f"Seu contrato foi renovado! Novo contrato: {novo_contrato.numero}.")
    return novo_contrato
