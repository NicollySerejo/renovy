import enum
import uuid
from datetime import datetime, date

from sqlalchemy import (
    Column, String, DateTime, Date, ForeignKey, Numeric, Enum, Boolean,
    Text, Table
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class UserRole(str, enum.Enum):
    cliente = "cliente"
    funcionario = "funcionario"
    administrador = "administrador"


class ContractStatus(str, enum.Enum):
    vigente = "vigente"
    proximo_vencimento = "proximo_vencimento"
    em_renovacao = "em_renovacao"
    aguardando_assinatura_cliente = "aguardando_assinatura_cliente"
    aguardando_assinatura_empresa = "aguardando_assinatura_empresa"
    renovado = "renovado"          # contrato antigo, substituido por um novo
    vencido = "vencido"
    cancelado = "cancelado"


class RenewalType(str, enum.Enum):
    aditivo = "aditivo"
    completa = "completa"


class RenewalStatus(str, enum.Enum):
    iniciada = "iniciada"
    em_preenchimento = "em_preenchimento"
    aguardando_assinatura_cliente = "aguardando_assinatura_cliente"
    aguardando_assinatura_empresa = "aguardando_assinatura_empresa"
    concluida = "concluida"
    cancelada = "cancelada"


class SignatureType(str, enum.Enum):
    cliente = "cliente"
    empresa = "empresa"


# ---------------------------------------------------------------------------
# Associacao Cliente <-> Paciente (N:N -- um responsavel pode ter varios
# pacientes e, futuramente, um paciente poderia ter mais de um responsavel)
# ---------------------------------------------------------------------------

client_patients = Table(
    "client_patients",
    Base.metadata,
    Column("client_id", UUID(as_uuid=False), ForeignKey("users.id"), primary_key=True),
    Column("patient_id", UUID(as_uuid=False), ForeignKey("patients.id"), primary_key=True),
)


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    nome = Column(String(255), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    telefone = Column(String(20), nullable=True)
    senha_hash = Column(String(255), nullable=True)  # null ate o "primeiro acesso"
    role = Column(Enum(UserRole), nullable=False, default=UserRole.cliente)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patients = relationship("Patient", secondary=client_patients, back_populates="clients")
    contracts = relationship("Contract", back_populates="client", foreign_keys="Contract.client_id")
    notifications = relationship("Notification", back_populates="user")


# ---------------------------------------------------------------------------
# Patient
# ---------------------------------------------------------------------------

class Patient(Base):
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    nome = Column(String(255), nullable=False)
    data_nascimento = Column(Date, nullable=True)
    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    clients = relationship("User", secondary=client_patients, back_populates="patients")
    contracts = relationship("Contract", back_populates="patient")


# ---------------------------------------------------------------------------
# Contract
# ---------------------------------------------------------------------------

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    numero = Column(String(50), unique=True, nullable=False)

    client_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=False), ForeignKey("patients.id"), nullable=False)

    tipo = Column(String(50), default="padrao")  # linha de servico/plano contratado
    status = Column(Enum(ContractStatus), nullable=False, default=ContractStatus.vigente)

    valor = Column(Numeric(10, 2), nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    condicoes = Column(Text, nullable=True)

    tipo_proxima_renovacao = Column(Enum(RenewalType), default=RenewalType.aditivo)

    # conteudo "documento" do contrato (HTML simples, renderizado/baixado como PDF)
    documento_html = Column(Text, nullable=True)

    # encadeamento de historico: aponta para o contrato que este substituiu
    contrato_anterior_id = Column(UUID(as_uuid=False), ForeignKey("contracts.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("User", back_populates="contracts", foreign_keys=[client_id])
    patient = relationship("Patient", back_populates="contracts")
    renewals = relationship("Renewal", back_populates="contract", foreign_keys="Renewal.contract_id")
    documents = relationship("Document", back_populates="contract")
    signatures = relationship("Signature", back_populates="contract")


# ---------------------------------------------------------------------------
# Renewal
# ---------------------------------------------------------------------------

class Renewal(Base):
    __tablename__ = "renewals"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    contract_id = Column(UUID(as_uuid=False), ForeignKey("contracts.id"), nullable=False)
    novo_contract_id = Column(UUID(as_uuid=False), ForeignKey("contracts.id"), nullable=True)

    tipo = Column(Enum(RenewalType), nullable=False)
    status = Column(Enum(RenewalStatus), nullable=False, default=RenewalStatus.iniciada)

    # payload livre com os dados preenchidos ao longo do fluxo (aditivo ou
    # etapas da renovacao completa) - simplifica o schema para o MVP
    dados_json = Column(Text, nullable=True)

    initiated_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    initiated_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    contract = relationship("Contract", back_populates="renewals", foreign_keys=[contract_id])
    documents = relationship("Document", back_populates="renewal")
    signatures = relationship("Signature", back_populates="renewal")


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    contract_id = Column(UUID(as_uuid=False), ForeignKey("contracts.id"), nullable=True)
    renewal_id = Column(UUID(as_uuid=False), ForeignKey("renewals.id"), nullable=True)
    uploaded_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)

    nome = Column(String(255), nullable=False)
    tipo = Column(String(100), nullable=True)  # ex: RG, comprovante_endereco, etc.
    caminho = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    contract = relationship("Contract", back_populates="documents")
    renewal = relationship("Renewal", back_populates="documents")


# ---------------------------------------------------------------------------
# Signature
# ---------------------------------------------------------------------------

class Signature(Base):
    __tablename__ = "signatures"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    contract_id = Column(UUID(as_uuid=False), ForeignKey("contracts.id"), nullable=True)
    renewal_id = Column(UUID(as_uuid=False), ForeignKey("renewals.id"), nullable=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)

    tipo = Column(Enum(SignatureType), nullable=False)
    nome_assinante = Column(String(255), nullable=False)
    data_hora = Column(DateTime, default=datetime.utcnow)
    hash_confirmacao = Column(String(255), nullable=False)  # "assinatura" simulada

    contract = relationship("Contract", back_populates="signatures")
    renewal = relationship("Renewal", back_populates="signatures")


# ---------------------------------------------------------------------------
# Notification
# ---------------------------------------------------------------------------

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    mensagem = Column(String(500), nullable=False)
    lida = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
