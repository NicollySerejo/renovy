import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.config import settings
from app import models, schemas

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=schemas.DocumentOut)
async def upload_document(
    file: UploadFile = File(...),
    tipo: str = Form(default="outro"),
    contract_id: str | None = Form(default=None),
    renewal_id: str | None = Form(default=None),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Recebe um arquivo do seletor nativo do dispositivo (input type=file,
    com 'capture' habilitado no front para permitir foto direto da camera).
    Formatos aceitos sao configuraveis em settings.ALLOWED_UPLOAD_EXTENSIONS."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Formato nao permitido. Aceitos: {', '.join(sorted(settings.ALLOWED_UPLOAD_EXTENSIONS))}",
        )

    if contract_id:
        contract = db.query(models.Contract).filter(models.Contract.id == contract_id).first()
        if not contract or (user.role == models.UserRole.cliente and contract.client_id != user.id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado a este contrato.")

    safe_name = f"{uuid.uuid4()}{ext}"
    dest_path = os.path.join(settings.UPLOAD_DIR, safe_name)
    content = await file.read()
    with open(dest_path, "wb") as f:
        f.write(content)

    doc = models.Document(
        contract_id=contract_id,
        renewal_id=renewal_id,
        uploaded_by=user.id,
        nome=file.filename or safe_name,
        tipo=tipo,
        caminho=dest_path,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/by-renewal/{renewal_id}", response_model=list[schemas.DocumentOut])
def list_by_renewal(
    renewal_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(models.Document).filter(models.Document.renewal_id == renewal_id).all()


@router.get("/by-contract/{contract_id}", response_model=list[schemas.DocumentOut])
def list_by_contract(
    contract_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(models.Document).filter(models.Document.contract_id == contract_id).all()
