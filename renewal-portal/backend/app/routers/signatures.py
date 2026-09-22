from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.security import signature_hash
from app.services.renewal_flow import finalizar_renovacao
from app.services.notify import notify
from app import models, schemas

router = APIRouter(prefix="/signatures", tags=["signatures"])


@router.post("", response_model=schemas.SignatureOut)
def sign(
    payload: schemas.SignatureCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Assinatura eletronica simulada do MVP.

    Fluxo: 1) ler o documento (feito no front, via revisao) 2) confirmar que
    conferiu as informacoes (payload.confirmo_leitura) 3) assinar 4) confirmar.
    So registra a assinatura se o `confirmo_leitura` vier true.
    """
    if not payload.confirmo_leitura:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "E necessario confirmar a leitura do documento.")
    if not payload.renewal_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "renewal_id e obrigatorio.")

    renewal = db.query(models.Renewal).filter(models.Renewal.id == payload.renewal_id).first()
    if not renewal:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Renovacao nao encontrada.")
    contract = renewal.contract

    if payload.tipo == "cliente":
        if user.role != models.UserRole.cliente or contract.client_id != user.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Somente o responsavel pelo contrato pode assinar como cliente.")
        if renewal.status != models.RenewalStatus.aguardando_assinatura_cliente:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Esta renovacao nao esta aguardando a assinatura do cliente.")
    elif payload.tipo == "empresa":
        if user.role not in (models.UserRole.funcionario, models.UserRole.administrador):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Somente a empresa pode assinar como empresa.")
        if renewal.status != models.RenewalStatus.aguardando_assinatura_empresa:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Esta renovacao nao esta aguardando a assinatura da empresa.")
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Tipo de assinatura invalido.")

    now = datetime.utcnow()
    sig = models.Signature(
        contract_id=contract.id,
        renewal_id=renewal.id,
        user_id=user.id,
        tipo=models.SignatureType(payload.tipo),
        nome_assinante=payload.nome_assinante,
        data_hora=now,
        hash_confirmacao=signature_hash(user.id, renewal.id, now.isoformat()),
    )
    db.add(sig)

    if payload.tipo == "cliente":
        renewal.status = models.RenewalStatus.aguardando_assinatura_empresa
        contract.status = models.ContractStatus.aguardando_assinatura_empresa
        db.commit()
        notify(db, contract.client_id, "Recebemos sua assinatura. Aguardando a confirmacao da empresa.")
    else:
        db.commit()
        finalizar_renovacao(db, renewal)

    db.refresh(sig)
    return sig
