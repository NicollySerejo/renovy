import axios from "axios";

export const api = axios.create({ baseURL: "/api" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("role");
      localStorage.removeItem("nome");
      if (!location.pathname.startsWith("/login")) location.href = "/login";
    }
    return Promise.reject(err);
  }
);

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface Patient {
  id: string;
  nome: string;
  data_nascimento?: string | null;
}

export interface ClientMe {
  id: string;
  nome: string;
  cpf: string;
  email?: string;
  telefone?: string;
  role: string;
  patients: Patient[];
}

export interface Contract {
  id: string;
  numero: string;
  client_id: string;
  patient_id: string;
  tipo: string;
  status: string;
  valor: number;
  data_inicio: string;
  data_fim: string;
  condicoes?: string;
  tipo_proxima_renovacao: string;
  contrato_anterior_id?: string | null;
  dias_para_vencer?: number;
  created_at: string;
  cliente_nome?: string;
  paciente_nome?: string;
}

export interface Renewal {
  id: string;
  contract_id: string;
  novo_contract_id?: string | null;
  tipo: string;
  status: string;
  dados_json?: string;
  initiated_at: string;
  completed_at?: string | null;
}

export interface Notification {
  id: string;
  mensagem: string;
  lida: boolean;
  created_at: string;
}

export interface DashboardMetrics {
  total_clientes: number;
  contratos_vigentes: number;
  contratos_proximos_vencimento: number;
  renovacoes_em_andamento: number;
  renovacoes_concluidas: number;
  contratos_vencidos: number;
}

// ---------------------------------------------------------------------------
// Endpoints
// ---------------------------------------------------------------------------

export const AuthAPI = {
  identify: (data: { cpf: string; nome_completo: string; nome_paciente: string }) =>
    api.post("/auth/identify", data).then((r) => r.data),
  register: (data: { cpf: string; email: string; telefone: string; senha: string; confirmar_senha: string }) =>
    api.post("/auth/register", data).then((r) => r.data),
  login: (data: { identificador: string; senha: string }) =>
    api.post("/auth/login", data).then((r) => r.data),
};

export const ClientAPI = {
  me: () => api.get<ClientMe>("/clients/me").then((r) => r.data),
  notifications: () => api.get<Notification[]>("/clients/me/notifications").then((r) => r.data),
};

export const ContractAPI = {
  list: () => api.get<Contract[]>("/contracts").then((r) => r.data),
  get: (id: string) => api.get<Contract>(`/contracts/${id}`).then((r) => r.data),
  documentUrl: (id: string) => `/api/contracts/${id}/document`,
};

export const RenewalAPI = {
  start: (contract_id: string, tipo: "aditivo" | "completa") =>
    api.post<Renewal>("/renewals", { contract_id, tipo }).then((r) => r.data),
  get: (id: string) => api.get<Renewal>(`/renewals/${id}`).then((r) => r.data),
  updateAditivo: (id: string, data: any) => api.put<Renewal>(`/renewals/${id}/aditivo`, data).then((r) => r.data),
  updateEtapa: (id: string, etapa: string, dados: any) =>
    api.put<Renewal>(`/renewals/${id}/etapa`, { etapa, dados }).then((r) => r.data),
  submit: (id: string) => api.post<Renewal>(`/renewals/${id}/submit`).then((r) => r.data),
  listAll: () => api.get<Renewal[]>("/renewals").then((r) => r.data),
};

export const DocumentAPI = {
  upload: (file: File, opts: { tipo?: string; contract_id?: string; renewal_id?: string }) => {
    const form = new FormData();
    form.append("file", file);
    if (opts.tipo) form.append("tipo", opts.tipo);
    if (opts.contract_id) form.append("contract_id", opts.contract_id);
    if (opts.renewal_id) form.append("renewal_id", opts.renewal_id);
    return api.post("/documents", form, { headers: { "Content-Type": "multipart/form-data" } }).then((r) => r.data);
  },
  byRenewal: (renewalId: string) => api.get(`/documents/by-renewal/${renewalId}`).then((r) => r.data),
};

export const SignatureAPI = {
  sign: (data: { renewal_id: string; tipo: "cliente" | "empresa"; nome_assinante: string; confirmo_leitura: boolean }) =>
    api.post("/signatures", data).then((r) => r.data),
};

export const AdminAPI = {
  dashboard: () => api.get<DashboardMetrics>("/admin/dashboard").then((r) => r.data),
  listClients: (q?: string) => api.get("/admin/clients", { params: { q } }).then((r) => r.data),
  createClient: (data: any) => api.post("/admin/clients", data).then((r) => r.data),
  createEmployee: (data: any) => api.post("/admin/employees", data).then((r) => r.data),
  listContracts: (params?: { q?: string; status?: string; order_by?: string }) =>
    api.get<Contract[]>("/admin/contracts", { params }).then((r) => r.data),
};
