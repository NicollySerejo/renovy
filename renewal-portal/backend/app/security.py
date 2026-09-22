import hashlib
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=expires_minutes or settings.JWT_EXPIRES_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None


def signature_hash(user_id: str, document_ref: str, timestamp: str) -> str:
    """Gera um identificador (hash) que simula a assinatura eletronica.

    NAO e uma assinatura digital com validade juridica de certificado (ICP-Brasil).
    Serve para registrar, de forma auditavel, que o usuario confirmou os dados
    em um determinado momento. Uma integracao futura com um provedor de
    assinatura eletronica (ex: Clicksign, DocuSign) pode substituir esta funcao.
    """
    raw = f"{user_id}|{document_ref}|{timestamp}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def only_digits(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


def validate_cpf(cpf: str) -> bool:
    """Validacao de CPF (digitos verificadores). Aceita string com ou sem mascara."""
    cpf = only_digits(cpf)
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False

    def calc_digit(cpf_partial: str) -> int:
        weight = len(cpf_partial) + 1
        total = sum(int(d) * (weight - i) for i, d in enumerate(cpf_partial))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    d1 = calc_digit(cpf[:9])
    d2 = calc_digit(cpf[:9] + str(d1))
    return cpf[-2:] == f"{d1}{d2}"
