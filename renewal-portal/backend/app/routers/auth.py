from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, security

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/identify", response_model=schemas.IdentifyResponse)
def identify(payload: schemas.IdentifyRequest, db: Session = Depends(get_db)):
    """Tela 'Identifique seu cadastro' do primeiro acesso.

    Confere CPF + nome + paciente contra um cadastro ja lancado pela empresa
    (via painel administrativo). Isso evita que qualquer pessoa crie uma
    conta nova sem ter sido previamente cadastrada como cliente.
    """
    cpf = security.only_digits(payload.cpf)
    user = db.query(models.User).filter(
        models.User.cpf == cpf, models.User.role == models.UserRole.cliente
    ).first()

    if not user:
        return schemas.IdentifyResponse(
            encontrado=False, primeiro_acesso=False,
            mensagem="Nao encontramos um cadastro com esses dados. Entre em contato com a empresa.",
        )

    nomes_batem = user.nome.strip().lower() == payload.nome_completo.strip().lower()
    paciente_batem = any(
        p.nome.strip().lower() == payload.nome_paciente.strip().lower() for p in user.patients
    )
    if not (nomes_batem and paciente_batem):
        return schemas.IdentifyResponse(
            encontrado=False, primeiro_acesso=False,
            mensagem="Os dados informados nao conferem com nosso cadastro.",
        )

    if user.senha_hash:
        return schemas.IdentifyResponse(
            encontrado=True, primeiro_acesso=False,
            mensagem="Cadastro ja possui acesso. Va para a tela de login.",
        )

    return schemas.IdentifyResponse(
        encontrado=True, primeiro_acesso=True,
        mensagem="Cadastro encontrado. Complete seu acesso.",
    )


@router.post("/register", response_model=schemas.TokenResponse)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    """Conclui o primeiro acesso: define e-mail/telefone/senha para um
    cadastro que a empresa ja criou previamente (ver /admin/clients)."""
    if payload.senha != payload.confirmar_senha:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "As senhas nao conferem.")

    cpf = security.only_digits(payload.cpf)
    user = db.query(models.User).filter(
        models.User.cpf == cpf, models.User.role == models.UserRole.cliente
    ).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cadastro nao encontrado.")
    if user.senha_hash:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Este cadastro ja possui acesso criado.")

    user.email = payload.email
    user.telefone = payload.telefone
    user.senha_hash = security.hash_password(payload.senha)
    db.commit()
    db.refresh(user)

    token = security.create_access_token({"sub": user.id, "role": user.role.value})
    return schemas.TokenResponse(access_token=token, role=user.role.value, nome=user.nome)


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    identificador = payload.identificador.strip()
    cpf_digits = security.only_digits(identificador)

    user = db.query(models.User).filter(
        (models.User.email == identificador) | (models.User.cpf == cpf_digits)
    ).first()

    if not user or not user.senha_hash or not security.verify_password(payload.senha, user.senha_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "CPF/e-mail ou senha invalidos.")
    if not user.ativo:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Usuario inativo.")

    token = security.create_access_token({"sub": user.id, "role": user.role.value})
    return schemas.TokenResponse(access_token=token, role=user.role.value, nome=user.nome)
