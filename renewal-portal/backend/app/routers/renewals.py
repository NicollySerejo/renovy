from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_staff
from app.services.renewal_flow import merge_dados
from app.services.notify import notify
from app import models, schemas

router = APIRouter(prefix="/renewals", tags=["renewals"])


def _get_contract_or_403(db: Session, contract_id: str, user: models.User) -> models.Contract:
    contract = db.query(models.Contract).filter(models.Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Contrato nao encontrado.")
    if user.role == models.UserRole.cliente and contract.client_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Voce nao tem acesso a este contrato.")
    return contract


@router.post("", response_model=schemas.RenewalOut)
def start_renewal(
    payload: schemas.RenewalCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Inicia uma renovacao. Pode ser disparado pelo cliente (a partir do
    alerta de vencimento) ou manualmente pela empresa (funcionario/admin)."""
    contract = _get_contract_or_403(db, payload.contract_id, user)

    if payload.tipo not in ("aditivo", "completa"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Tipo de renovacao invalido.")

    existente = (
        db.query(models.Renewal)
        .filter(
            models.Renewal.contract_id == contract.id,
            models.Renewal.status.notin_([models.RenewalStatus.concluida, models.RenewalStatus.cancelada]),
        )
        .first()
    )
    if existente:
        return existente

    renewal = models.Renewal(
        contract_id=contract.id,
        tipo=models.RenewalType(payload.tipo),
        status=models.RenewalStatus.em_preenchimento,
        initiated_by=user.id,
    )
    contract.status = models.ContractStatus.em_renovacao
    db.add(renewal)
    db.commit()
    db.refresh(renewal)
    notify(db, contract.client_id, "Sua renovacao esta disponivel. Complete as informacoes para continuar.")
    return renewal


@router.get("/{renewal_id}", response_model=schemas.RenewalOut)
def get_renewal(
    renewal_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    renewal = db.query(models.Renewal).filter(models.Renewal.id == renewal_id).first()
    if not renewal:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Renovacao nao encontrada.")
    _get_contract_or_403(db, renewal.contract_id, user)
    return renewal


@router.put("/{renewal_id}/aditivo", response_model=schemas.RenewalOut)
def update_aditivo(
    renewal_id: str,
    payload: schemas.RenewalUpdateAditivo,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    renewal = db.query(models.Renewal).filter(models.Renewal.id == renewal_id).first()
    if not renewal or renewal.tipo != models.RenewalType.aditivo:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Renovacao (aditivo) nao encontrada.")
    _get_contract_or_403(db, renewal.contract_id, user)

    merge_dados(renewal, payload.model_dump())
    db.commit()
    db.refresh(renewal)
    return renewal


@router.put("/{renewal_id}/etapa", response_model=schemas.RenewalOut)
def update_etapa_completa(
    renewal_id: str,
    payload: schemas.RenewalUpdateCompleta,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Salva os dados de uma etapa do formulario de renovacao completa
    (responsavel, paciente, endereco, contato, contratuais, documentos,
    revisao). Pode ser chamado varias vezes; o cliente pode voltar e editar
    etapas anteriores sem perder o que ja preencheu."""
    renewal = db.query(models.Renewal).filter(models.Renewal.id == renewal_id).first()
    if not renewal or renewal.tipo != models.RenewalType.completa:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Renovacao (completa) nao encontrada.")
    _get_contract_or_403(db, renewal.contract_id, user)

    merge_dados(renewal, payload.dados, etapa=payload.etapa)
    db.commit()
    db.refresh(renewal)
    return renewal


@router.post("/{renewal_id}/submit", response_model=schemas.RenewalOut)
def submit_for_signature(
    renewal_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cliente confirma que revisou todas as informacoes ('Confira todas as
    informacoes antes de continuar' / 'CONFIRMAR RENOVACAO'). Move a
    renovacao para aguardando a assinatura do cliente."""
    renewal = db.query(models.Renewal).filter(models.Renewal.id == renewal_id).first()
    if not renewal:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Renovacao nao encontrada.")
    contract = _get_contract_or_403(db, renewal.contract_id, user)

    renewal.status = models.RenewalStatus.aguardando_assinatura_cliente
    contract.status = models.ContractStatus.aguardando_assinatura_cliente
    db.commit()
    db.refresh(renewal)
    return renewal


@router.get("", response_model=list[schemas.RenewalOut])
def list_renewals(
    user: models.User = Depends(require_staff),
    db: Session = Depends(get_db),
):
    return db.query(models.Renewal).order_by(models.Renewal.initiated_at.desc()).all()
