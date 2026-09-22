"""Popula o banco com dados ficticios para demonstracao.

Uso:
    cd backend
    python seed.py
"""
from datetime import date, timedelta

from app.database import SessionLocal, Base, engine
from app import models
from app.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

def upsert_user(**kwargs):
    existing = db.query(models.User).filter(models.User.cpf == kwargs["cpf"]).first()
    if existing:
        return existing
    user = models.User(**kwargs)
    db.add(user)
    db.flush()
    return user


print("Criando usuarios de demonstracao...")

admin = upsert_user(
    nome="Ana Administradora", cpf="11111111111", email="admin@empresa.com",
    telefone="11999990001", role=models.UserRole.administrador,
    senha_hash=hash_password("admin123"),
)

funcionario = upsert_user(
    nome="Carlos Funcionario", cpf="22222222222", email="funcionario@empresa.com",
    telefone="11999990002", role=models.UserRole.funcionario,
    senha_hash=hash_password("func123"),
)

# Cliente 1: primeiro acesso ainda NAO realizado (senha_hash=None)
# -> serve para testar o fluxo de "Identifique seu cadastro"
cliente1 = upsert_user(
    nome="Maria da Silva", cpf="33333333333", email="maria@example.com",
    telefone="11999990003", role=models.UserRole.cliente, senha_hash=None,
)

# Cliente 2: ja com acesso criado -> serve para testar login direto
cliente2 = upsert_user(
    nome="Joao Pereira", cpf="44444444444", email="joao@example.com",
    telefone="11999990004", role=models.UserRole.cliente,
    senha_hash=hash_password("cliente123"),
)

db.flush()

print("Criando pacientes...")
if not cliente1.patients:
    p1 = models.Patient(nome="Joao da Silva", data_nascimento=date(2015, 3, 12))
    cliente1.patients.append(p1)
    db.add(p1)
else:
    p1 = cliente1.patients[0]

if not cliente2.patients:
    p2 = models.Patient(nome="Sofia Pereira", data_nascimento=date(2018, 7, 22))
    cliente2.patients.append(p2)
    db.add(p2)
else:
    p2 = cliente2.patients[0]

db.flush()

print("Criando contratos...")
hoje = date.today()


def upsert_contract(numero, **kwargs):
    existing = db.query(models.Contract).filter(models.Contract.numero == numero).first()
    if existing:
        return existing
    c = models.Contract(numero=numero, **kwargs)
    db.add(c)
    db.flush()
    return c

# Contrato antigo (historico) do cliente 1
c1_antigo = upsert_contract(
    "CT-1000-2024", client_id=cliente1.id, patient_id=p1.id, tipo="padrao",
    status=models.ContractStatus.renovado, valor=3200.00,
    data_inicio=date(2024, 10, 10), data_fim=date(2025, 10, 10),
    condicoes="Atendimento semanal.", tipo_proxima_renovacao=models.RenewalType.aditivo,
)

# Contrato vigente do cliente 1, proximo do vencimento (ativa o fluxo de renovacao)
c1_atual = upsert_contract(
    "CT-1000-2025", client_id=cliente1.id, patient_id=p1.id, tipo="padrao",
    status=models.ContractStatus.vigente, valor=3500.00,
    data_inicio=date(2025, 10, 10), data_fim=hoje + timedelta(days=20),
    condicoes="Atendimento semanal.", tipo_proxima_renovacao=models.RenewalType.aditivo,
    contrato_anterior_id=c1_antigo.id,
)

# Contrato vigente do cliente 2, com bastante tempo ate o vencimento
upsert_contract(
    "CT-2000-2025", client_id=cliente2.id, patient_id=p2.id, tipo="padrao",
    status=models.ContractStatus.vigente, valor=2800.00,
    data_inicio=date(2025, 6, 1), data_fim=date(2026, 6, 1),
    condicoes="Atendimento quinzenal.", tipo_proxima_renovacao=models.RenewalType.completa,
)

db.commit()

print("\nSeed concluido!\n")
print("Contas de demonstracao:")
print("  Administrador -> CPF/e-mail: admin@empresa.com | senha: admin123")
print("  Funcionario   -> CPF/e-mail: funcionario@empresa.com | senha: func123")
print("  Cliente (com acesso) -> CPF/e-mail: joao@example.com | senha: cliente123")
print("  Cliente (primeiro acesso) -> CPF: 333.333.333-33 | Nome: Maria da Silva | Paciente: Joao da Silva")

db.close()
