from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_staff, require_admin
from app.security import hash_password, only_digits, validate_cpf
from app.config import settings
from app import models, schemas

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=schemas.AdminDashboardOut)
def dashboard(user: models.User = Depends(require_staff), db: Session = Depends(get_db)):
    hoje = date.today()
    limite = hoje + timedelta(days=settings.DIAS_ALERTA_VENCIMENTO)

    total_clientes = db.query(models.User).filter(models.User.role == models.UserRole.cliente).count()
    contratos_vigentes = db.query(models.Contract).filter(models.Contract.status == models.ContractStatus.vigente).count()
    contratos_proximos = db.query(models.Contract).filter(
        models.Contract.status == models.ContractStatus.proximo_vencimento
    ).count()
    renovacoes_andamento = db.query(models.Renewal).filter(
        models.Renewal.status.notin_([models.RenewalStatus.concluida, models.RenewalStatus.cancelada])
    ).count()
    renovacoes_concluidas = db.query(models.Renewal).filter(
        models.Renewal.status == models.RenewalStatus.concluida
    ).count()
    contratos_vencidos = db.query(models.Contract).filter(models.Contract.status == models.ContractStatus.vencido).count()

    return schemas.AdminDashboardOut(
        total_clientes=total_clientes,
        contratos_vigentes=contratos_vigentes,
        contratos_proximos_vencimento=contratos_proximos,
        renovacoes_em_andamento=renovacoes_andamento,
        renovacoes_concluidas=renovacoes_concluidas,
        contratos_vencidos=contratos_vencidos,
    )


@router.get("/clients", response_model=list[schemas.ClientMeOut])
def list_clients(
    q: str | None = Query(default=None, description="busca por nome ou CPF"),
    user: models.User = Depends(require_staff),
    db: Session = Depends(get_db),
):
    query = db.query(models.User).filter(models.User.role == models.UserRole.cliente)
    if q:
        like = f"%{q}%"
        query = query.filter((models.User.nome.ilike(like)) | (models.User.cpf.ilike(like)))
    return query.order_by(models.User.nome).all()


@router.post("/clients", response_model=schemas.ContractOut)
def create_client(
    payload: schemas.ClientCreate,
    user: models.User = Depends(require_staff),
    db: Session = Depends(get_db),
):
    """Cadastra responsavel + paciente + primeiro contrato em uma unica
    operacao (tela 'Cadastro de cliente' da area administrativa)."""
    cpf = only_digits(payload.cpf)
    if not validate_cpf(cpf):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "CPF invalido.")
    if db.query(models.User).filter(models.User.cpf == cpf).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Ja existe um cadastro com este CPF.")

    client = models.User(
        nome=payload.nome,
        cpf=cpf,
        email=payload.email,
        telefone=payload.telefone,
        role=models.UserRole.cliente,
        senha_hash=None,  # definida no "primeiro acesso"
    )
    patient = models.Patient(nome=payload.paciente_nome, data_nascimento=payload.paciente_data_nascimento)
    client.patients.append(patient)
    db.add(client)
    db.add(patient)
    db.flush()

    if db.query(models.Contract).filter(models.Contract.numero == payload.contrato_numero).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Ja existe um contrato com este numero.")

    contract = models.Contract(
        numero=payload.contrato_numero,
        client_id=client.id,
        patient_id=patient.id,
        tipo=payload.contrato_tipo,
        status=models.ContractStatus.vigente,
        valor=payload.contrato_valor,
        data_inicio=payload.contrato_data_inicio,
        data_fim=payload.contrato_data_fim,
        condicoes=payload.contrato_condicoes,
        tipo_proxima_renovacao=models.RenewalType(payload.tipo_proxima_renovacao),
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)

    from app.routers.contracts import _to_out
    return _to_out(contract)


@router.post("/employees", response_model=schemas.UserOut)
def create_employee(
    payload: schemas.EmployeeCreate,
    user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if payload.role not in ("funcionario", "administrador"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Papel invalido.")
    cpf = only_digits(payload.cpf)
    if not validate_cpf(cpf):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "CPF invalido.")
    if db.query(models.User).filter(models.User.cpf == cpf).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Ja existe um cadastro com este CPF.")

    employee = models.User(
        nome=payload.nome,
        cpf=cpf,
        email=payload.email,
        telefone=payload.telefone,
        role=models.UserRole(payload.role),
        senha_hash=hash_password(payload.senha),
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@router.delete("/employees/{employee_id}")
def remove_employee(
    employee_id: str,
    user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    employee = db.query(models.User).filter(
        models.User.id == employee_id, models.User.role != models.UserRole.cliente
    ).first()
    if not employee:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Funcionario nao encontrado.")
    employee.ativo = False
    db.commit()
    return {"ok": True}


@router.get("/contracts", response_model=list[schemas.ContractDetailOut])
def list_all_contracts(
    q: str | None = Query(default=None),
    status_filtro: str | None = Query(default=None, alias="status"),
    order_by: str = Query(default="data_fim"),
    user: models.User = Depends(require_staff),
    db: Session = Depends(get_db),
):
    from app.services.status import calcular_status_automatico

    query = db.query(models.Contract)
    if status_filtro:
        query = query.filter(models.Contract.status == status_filtro)
    contracts = query.all()

    changed = False
    for c in contracts:
        novo = calcular_status_automatico(c)
        if novo != c.status:
            c.status = novo
            changed = True
    if changed:
        db.commit()

    if q:
        ql = q.lower()
        contracts = [
            c for c in contracts
            if ql in c.client.nome.lower() or ql in c.patient.nome.lower() or ql in c.numero.lower()
        ]

    reverse = order_by.startswith("-")
    field = order_by.lstrip("-")
    key_map = {
        "data_fim": lambda c: c.data_fim,
        "data_inicio": lambda c: c.data_inicio,
        "valor": lambda c: float(c.valor),
        "cliente": lambda c: c.client.nome,
    }
    if field in key_map:
        contracts.sort(key=key_map[field], reverse=reverse)

    from app.routers.contracts import _to_out
    result = []
    for c in contracts:
        base = _to_out(c)
        result.append(schemas.ContractDetailOut(**base.model_dump(), cliente_nome=c.client.nome, paciente_nome=c.patient.nome))
    return result
