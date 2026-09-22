# Portal de Renovação de Contratos — MVP

Sistema web para automatizar a renovação anual de contratos de clientes/responsáveis
vinculados a pacientes, substituindo o processo manual por WhatsApp/e-mail por um
portal online.

## Stack

- **Frontend:** React + TypeScript + Vite
- **Backend:** Python + FastAPI
- **Banco de dados:** PostgreSQL (via SQLAlchemy)
- **Autenticação:** JWT + senhas com hash (bcrypt)

## Estrutura do projeto

```
renewal-portal/
├── backend/
│   ├── app/
│   │   ├── main.py          # ponto de entrada da API
│   │   ├── config.py        # variáveis de ambiente
│   │   ├── database.py      # engine/session do SQLAlchemy
│   │   ├── models.py        # entidades (User, Patient, Contract, Renewal, Document, Signature, Notification)
│   │   ├── schemas.py       # schemas Pydantic (request/response)
│   │   ├── security.py      # hash de senha, JWT, validação de CPF
│   │   ├── deps.py          # dependências de autenticação/autorização
│   │   ├── routers/         # auth, clients, contracts, renewals, documents, signatures, admin
│   │   └── services/        # regras de status/vencimento, geração de documento, notificações, fluxo de renovação
│   ├── seed.py               # popula o banco com dados fictícios
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/client.ts     # cliente HTTP (axios) tipado
│   │   ├── context/AuthContext.tsx
│   │   ├── components/       # Layout, ExpiryRing, StatusBadge, ProtectedRoute
│   │   └── pages/            # Landing, FirstAccess, Login, ClientDashboard, ContractView,
│   │                         # History, RenewalFlow (+ renewal/*), AdminDashboard, AdminClientNew
│   └── package.json
└── docker-compose.yml         # sobe apenas o PostgreSQL
```

## Pré-requisitos

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (local, via Docker, ou um serviço gerenciado)

## 1. Banco de dados

Opção mais simples — subir o Postgres com Docker:

```bash
docker compose up -d
```

Isso cria o banco `renewal_portal` com usuário `portal_user` / senha `portal_pass`
na porta `5432` (ver `docker-compose.yml`). Se preferir usar um Postgres já
instalado localmente, apenas crie um banco e ajuste `DATABASE_URL` no passo 2.

## 2. Backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env             # ajuste DATABASE_URL/JWT_SECRET_KEY se necessário

# cria as tabelas e sobe a API
uvicorn app.main:app --reload --port 8000

# em outro terminal, com o venv ativado, popule dados de demonstração:
python seed.py
```

A API sobe em `http://localhost:8000`. Documentação interativa (Swagger) em
`http://localhost:8000/docs`.

## 3. Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

O frontend sobe em `http://localhost:5173` e já está configurado (`vite.config.ts`)
para redirecionar chamadas `/api/*` para o backend em `http://localhost:8000`.

## Contas de demonstração (criadas pelo `seed.py`)

| Perfil | Login | Senha |
|---|---|---|
| Administrador | admin@empresa.com | admin123 |
| Funcionário | funcionario@empresa.com | func123 |
| Cliente (já com acesso) | joao@example.com | cliente123 |
| Cliente (primeiro acesso) | CPF `333.333.333-33`, nome "Maria da Silva", paciente "Joao da Silva" | — (crie sua senha na tela de primeiro acesso) |

Use a conta de "primeiro acesso" para testar o fluxo completo de identificação →
criação de senha → login. Use `joao@example.com` para testar login direto, e as
contas de administrador/funcionário para o painel administrativo e para assinar
como empresa no fluxo de renovação.

## Fluxo ponta a ponta para demonstrar

1. Login como funcionário/admin → **Painel administrativo** → conferir métricas e
   a tabela de contratos.
2. Login como `joao@example.com` (ou complete o primeiro acesso de Maria) →
   **Minha área** → contrato próximo do vencimento → **Iniciar renovação**.
3. Preencher o aditivo (ou as etapas da renovação completa, dependendo do
   `tipo_proxima_renovacao` do contrato) → **Confirmar renovação**.
4. Assinar como cliente. O sistema muda o status para "aguardando a empresa".
5. Logar como funcionário/admin, abrir a mesma renovação (`/admin` → contrato →
   ou acessar `/renovacao/<id>` diretamente) e assinar como empresa.
6. Ao concluir as duas assinaturas, um **novo contrato** é criado
   automaticamente (o antigo é preservado com status "renovado") e aparece no
   histórico do cliente.

## Decisões e limitações do MVP (o que fica para próximas etapas)

- **Documento do contrato:** por não haver uma biblioteca de PDF instalada no
  ambiente em que este código foi gerado, o "PDF" do contrato é servido como
  HTML pronto para impressão/"Salvar como PDF" pelo navegador
  (`app/services/documents.py`). Trocar por geração real de PDF (WeasyPrint,
  ReportLab) é uma mudança isolada nesse arquivo.
- **Assinatura eletrônica:** é uma assinatura interna simulada (registra nome,
  data/hora, usuário e um hash de confirmação) — não é uma assinatura com
  certificado ICP-Brasil. Uma integração futura com um provedor (Clicksign,
  DocuSign, etc.) pode substituir `app/routers/signatures.py`.
- **Notificações:** apenas internas (tabela `notifications`, endpoint
  `GET /clients/me/notifications`). O código já está estruturado para receber
  canais externos (e-mail, WhatsApp, push) futuramente, mas essas integrações
  não foram implementadas.
- **Rotina de vencimento:** o status do contrato (vigente → próximo do
  vencimento → vencido) é recalculado automaticamente sempre que os contratos
  são listados/consultados (`app/services/status.py`). Para dispará-lo também
  em background (ex.: para dispor notificações diárias mesmo sem acesso do
  usuário), adicione um scheduler (ex. APScheduler ou um cron chamando um
  endpoint) chamando essa mesma função periodicamente.
- **Migrações:** o MVP cria as tabelas com `Base.metadata.create_all` na
  inicialização, para simplificar a primeira execução. Para evoluir o schema
  com segurança em produção, migre para Alembic.
- **Upload de documentos:** os arquivos são salvos em disco local
  (`backend/uploads/`) referenciados na tabela `documents`. A integração com
  Google Drive/iCloud mencionada no briefing não foi implementada, mas a
  tabela `documents` já foi desenhada para comportar uma origem externa no
  futuro.

## Segurança implementada

- Senhas nunca armazenadas em texto puro (hash bcrypt via `passlib`).
- Autenticação via JWT (`python-jose`), com expiração configurável.
- Autorização por papel (`cliente` / `funcionario` / `administrador`) em cada
  rota sensível (`app/deps.py`).
- Cliente só acessa os próprios dados (contratos filtrados por `client_id` em
  todas as rotas do lado do cliente).
- Validação de CPF (dígitos verificadores) no cadastro.
- `.env` fora do controle de versão (`.gitignore`); use `JWT_SECRET_KEY` forte
  em produção e habilite HTTPS no proxy/servidor de produção.
