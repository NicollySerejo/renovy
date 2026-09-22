from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.services.status import calcular_status_automatico, dias_para_vencer
from app.services.documents import render_contrato_html
from app import models, schemas

router = APIRouter(prefix="/contracts", tags=["contracts"])


def _to_out(contract: models.Contract) -> schemas.ContractOut:
    return schemas.ContractOut(
        id=contract.id,
        numero=contract.numero,
        client_id=contract.client_id,
        patient_id=contract.patient_id,
        tipo=contract.tipo,
        status=contract.status.value,
        valor=float(contract.valor),
        data_inicio=contract.data_inicio,
        data_fim=contract.data_fim,
        condicoes=contract.condicoes,
        tipo_proxima_renovacao=contract.tipo_proxima_renovacao.value,
        contrato_anterior_id=contract.contrato_anterior_id,
        dias_para_vencer=dias_para_vencer(contract.data_fim),
        created_at=contract.created_at,
    )


def _assert_can_view(contract: models.Contract, user: models.User):
    if user.role == models.UserRole.cliente and contract.client_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Voce nao tem acesso a este contrato.")


@router.get("", response_model=list[schemas.ContractOut])
def list_contracts(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cliente ve apenas os proprios contratos (historico incluido).
    Funcionario/administrador usam /admin/contracts para a visao geral."""
    query = db.query(models.Contract)
    if user.role == models.UserRole.cliente:
        query = query.filter(models.Contract.client_id == user.id)
    contracts = query.order_by(models.Contract.data_inicio.desc()).all()

    # recalcula status automatico "on read" para refletir a data atual
    changed = False
    for c in contracts:
        novo = calcular_status_automatico(c)
        if novo != c.status:
            c.status = novo
            changed = True
    if changed:
        db.commit()

    return [_to_out(c) for c in contracts]


@router.get("/{contract_id}", response_model=schemas.ContractDetailOut)
def get_contract(
    contract_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contract = db.query(models.Contract).filter(models.Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Contrato nao encontrado.")
    _assert_can_view(contract, user)

    novo_status = calcular_status_automatico(contract)
    if novo_status != contract.status:
        contract.status = novo_status
        db.commit()

    out = _to_out(contract)
    return schemas.ContractDetailOut(
        **out.model_dump(),
        cliente_nome=contract.client.nome,
        paciente_nome=contract.patient.nome,
    )


@router.get("/{contract_id}/document", response_class=HTMLResponse)
def get_contract_document(
    contract_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna o contrato renderizado em HTML (o navegador pode 'Imprimir >
    Salvar como PDF'). Ver app/services/documents.py para trocar por geracao
    de PDF real futuramente."""
    contract = db.query(models.Contract).filter(models.Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Contrato nao encontrado.")
    _assert_can_view(contract, user)
    return HTMLResponse(content=render_contrato_html(contract))
