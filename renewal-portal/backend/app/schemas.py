from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class IdentifyRequest(BaseModel):
    cpf: str
    nome_completo: str
    nome_paciente: str


class IdentifyResponse(BaseModel):
    encontrado: bool
    primeiro_acesso: bool
    mensagem: str


class RegisterRequest(BaseModel):
    cpf: str
    email: EmailStr
    telefone: str
    senha: str = Field(min_length=8)
    confirmar_senha: str


class LoginRequest(BaseModel):
    identificador: str  # cpf ou e-mail
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    nome: str


# ---------------------------------------------------------------------------
# User / Client
# ---------------------------------------------------------------------------

class PatientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nome: str
    data_nascimento: Optional[date] = None
    observacoes: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nome: str
    cpf: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    role: str
    ativo: bool


class ClientMeOut(UserOut):
    patients: List[PatientOut] = []


class ClientCreate(BaseModel):
    nome: str
    cpf: str
    email: EmailStr
    telefone: str
    paciente_nome: str
    paciente_data_nascimento: Optional[date] = None
    # dados do primeiro contrato
    contrato_numero: str
    contrato_valor: float
    contrato_data_inicio: date
    contrato_data_fim: date
    contrato_tipo: str = "padrao"
    contrato_condicoes: Optional[str] = None
    tipo_proxima_renovacao: str = "aditivo"


class EmployeeCreate(BaseModel):
    nome: str
    cpf: str
    email: EmailStr
    telefone: str
    senha: str = Field(min_length=8)
    role: str = "funcionario"  # ou "administrador"


# ---------------------------------------------------------------------------
# Contract
# ---------------------------------------------------------------------------

class ContractOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    numero: str
    client_id: str
    patient_id: str
    tipo: str
    status: str
    valor: float
    data_inicio: date
    data_fim: date
    condicoes: Optional[str] = None
    tipo_proxima_renovacao: str
    contrato_anterior_id: Optional[str] = None
    dias_para_vencer: Optional[int] = None
    created_at: datetime


class ContractDetailOut(ContractOut):
    cliente_nome: Optional[str] = None
    paciente_nome: Optional[str] = None


class ContractAdminCreate(BaseModel):
    client_id: str
    patient_id: str
    numero: str
    valor: float
    data_inicio: date
    data_fim: date
    tipo: str = "padrao"
    condicoes: Optional[str] = None
    tipo_proxima_renovacao: str = "aditivo"


# ---------------------------------------------------------------------------
# Renewal
# ---------------------------------------------------------------------------

class RenewalCreate(BaseModel):
    contract_id: str
    tipo: str  # "aditivo" | "completa"


class RenewalUpdateAditivo(BaseModel):
    novo_valor: Optional[float] = None
    nova_data_inicio: Optional[date] = None
    nova_data_fim: Optional[date] = None
    novos_dados_cadastrais: Optional[dict] = None


class RenewalUpdateCompleta(BaseModel):
    etapa: str  # responsavel | paciente | endereco | contato | contratuais | documentos | revisao
    dados: dict


class RenewalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    contract_id: str
    novo_contract_id: Optional[str] = None
    tipo: str
    status: str
    dados_json: Optional[str] = None
    initiated_at: datetime
    completed_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nome: str
    tipo: Optional[str] = None
    caminho: str
    uploaded_at: datetime


# ---------------------------------------------------------------------------
# Signature
# ---------------------------------------------------------------------------

class SignatureCreate(BaseModel):
    renewal_id: Optional[str] = None
    contract_id: Optional[str] = None
    tipo: str  # "cliente" | "empresa"
    nome_assinante: str
    confirmo_leitura: bool


class SignatureOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tipo: str
    nome_assinante: str
    data_hora: datetime


# ---------------------------------------------------------------------------
# Notification
# ---------------------------------------------------------------------------

class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    mensagem: str
    lida: bool
    created_at: datetime


# ---------------------------------------------------------------------------
# Admin dashboard
# ---------------------------------------------------------------------------

class AdminDashboardOut(BaseModel):
    total_clientes: int
    contratos_vigentes: int
    contratos_proximos_vencimento: int
    renovacoes_em_andamento: int
    renovacoes_concluidas: int
    contratos_vencidos: int
