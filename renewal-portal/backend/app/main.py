from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import auth, clients, contracts, renewals, documents, signatures, admin

# Cria as tabelas automaticamente no MVP (em producao, prefira Alembic para
# gerenciar migracoes de forma controlada).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Portal de Renovacao de Contratos - API",
    version="0.1.0",
    description="API do MVP para automatizar a renovacao anual de contratos.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(contracts.router)
app.include_router(renewals.router)
app.include_router(documents.router)
app.include_router(signatures.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"status": "ok"}
