import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import StatusBadge from "../components/StatusBadge";
import { AdminAPI, RenewalAPI, DashboardMetrics, Contract } from "../api/client";

const METRIC_LABELS: [keyof DashboardMetrics, string][] = [
  ["total_clientes", "Total de clientes"],
  ["contratos_vigentes", "Contratos vigentes"],
  ["contratos_proximos_vencimento", "Próximos do vencimento"],
  ["renovacoes_em_andamento", "Renovações em andamento"],
  ["renovacoes_concluidas", "Renovações concluídas"],
  ["contratos_vencidos", "Contratos vencidos"],
];

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [q, setQ] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [orderBy, setOrderBy] = useState("data_fim");

  function loadContracts() {
    AdminAPI.listContracts({ q: q || undefined, status: statusFilter || undefined, order_by: orderBy }).then(setContracts);
  }

  useEffect(() => {
    AdminAPI.dashboard().then(setMetrics);
    loadContracts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    loadContracts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter, orderBy]);

  async function iniciarRenovacaoManual(c: Contract) {
    const renewal = await RenewalAPI.start(c.id, c.tipo_proxima_renovacao as "aditivo" | "completa");
    navigate(`/renovacao/${renewal.id}`);
  }

  return (
    <Layout>
      <div className="row-between">
        <h2>Painel administrativo</h2>
        <Link to="/admin/clientes/novo" className="btn btn-primary">Cadastrar cliente</Link>
      </div>

      <div className="grid-2 mt-16" style={{ gridTemplateColumns: "repeat(3, 1fr)" }}>
        {metrics && METRIC_LABELS.map(([key, label]) => (
          <div key={key} className="card card-sm">
            <p className="muted" style={{ margin: 0 }}>{label}</p>
            <h3 style={{ margin: "6px 0 0" }}>{metrics[key]}</h3>
          </div>
        ))}
      </div>

      <div className="row mt-32" style={{ flexWrap: "wrap" }}>
        <input
          placeholder="Pesquisar cliente, paciente ou número do contrato"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && loadContracts()}
          style={{ flex: "1 1 260px", padding: "10px 14px", borderRadius: 8, border: "1.5px solid var(--border)" }}
        />
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} style={{ padding: "10px 14px", borderRadius: 8, border: "1.5px solid var(--border)" }}>
          <option value="">Todos os status</option>
          <option value="vigente">Vigente</option>
          <option value="proximo_vencimento">Próximo do vencimento</option>
          <option value="em_renovacao">Em renovação</option>
          <option value="aguardando_assinatura_cliente">Aguardando cliente</option>
          <option value="aguardando_assinatura_empresa">Aguardando empresa</option>
          <option value="renovado">Renovado</option>
          <option value="vencido">Vencido</option>
        </select>
        <select value={orderBy} onChange={(e) => setOrderBy(e.target.value)} style={{ padding: "10px 14px", borderRadius: 8, border: "1.5px solid var(--border)" }}>
          <option value="data_fim">Ordenar por vencimento</option>
          <option value="valor">Ordenar por valor</option>
          <option value="cliente">Ordenar por cliente</option>
        </select>
        <button className="btn btn-secondary" onClick={loadContracts}>Pesquisar</button>
      </div>

      <div className="card mt-16" style={{ padding: 0, overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "var(--surface-sunken)", textAlign: "left" }}>
              {["Cliente", "Paciente", "Vencimento", "Tipo", "Status", "Ações"].map((h) => (
                <th key={h} style={{ padding: "12px 16px", fontSize: "0.8rem", color: "var(--ink-soft)" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {contracts.map((c) => (
              <tr key={c.id} style={{ borderTop: "1px solid var(--border)" }}>
                <td style={{ padding: "12px 16px" }}>{c.cliente_nome}</td>
                <td style={{ padding: "12px 16px" }}>{c.paciente_nome}</td>
                <td style={{ padding: "12px 16px" }}>{new Date(c.data_fim).toLocaleDateString("pt-BR")}</td>
                <td style={{ padding: "12px 16px" }}>{c.tipo_proxima_renovacao}</td>
                <td style={{ padding: "12px 16px" }}><StatusBadge status={c.status} /></td>
                <td style={{ padding: "12px 16px" }}>
                  <div className="row">
                    <Link to={`/contratos/${c.id}`} className="btn btn-ghost">Abrir</Link>
                    {(c.status === "vigente" || c.status === "proximo_vencimento") && (
                      <button className="btn btn-ghost" onClick={() => iniciarRenovacaoManual(c)}>Iniciar renovação</button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
            {contracts.length === 0 && (
              <tr><td colSpan={6} style={{ padding: 20, textAlign: "center" }} className="muted">Nenhum contrato encontrado.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </Layout>
  );
}
