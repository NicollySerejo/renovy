import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Layout from "../components/Layout";
import ExpiryRing from "../components/ExpiryRing";
import StatusBadge from "../components/StatusBadge";
import { ClientAPI, ContractAPI, RenewalAPI, ClientMe, Contract } from "../api/client";

export default function ClientDashboard() {
  const [me, setMe] = useState<ClientMe | null>(null);
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    Promise.all([ClientAPI.me(), ContractAPI.list()]).then(([meRes, contractsRes]) => {
      setMe(meRes);
      setContracts(contractsRes);
      setLoading(false);
    });
  }, []);

  const atual = contracts.find((c) =>
    ["vigente", "proximo_vencimento", "em_renovacao", "aguardando_assinatura_cliente", "aguardando_assinatura_empresa"].includes(c.status)
  );

  async function iniciarRenovacao() {
    if (!atual) return;
    setStarting(true);
    try {
      const renewal = await RenewalAPI.start(atual.id, atual.tipo_proxima_renovacao as "aditivo" | "completa");
      window.location.href = `/renovacao/${renewal.id}`;
    } finally {
      setStarting(false);
    }
  }

  if (loading) return <Layout><p className="muted">Carregando...</p></Layout>;

  const paciente = me?.patients[0];

  return (
    <Layout>
      <h2>Olá, {me?.nome.split(" ")[0]}!</h2>
      {paciente && <p className="muted">Você é responsável por {paciente.nome}.</p>}

      {atual ? (
        <div className="card mt-16">
          <div className="row-between">
            <div>
              <p className="muted" style={{ marginBottom: 4 }}>Contrato {atual.numero}</p>
              <h3 style={{ margin: "0 0 8px" }}>Contrato atual</h3>
              <StatusBadge status={atual.status} />
            </div>
            <ExpiryRing days={atual.dias_para_vencer ?? 0} />
          </div>

          <div className="grid-2 mt-16">
            <div>
              <p className="muted" style={{ margin: 0 }}>Início</p>
              <strong>{new Date(atual.data_inicio).toLocaleDateString("pt-BR")}</strong>
            </div>
            <div>
              <p className="muted" style={{ margin: 0 }}>Vencimento</p>
              <strong>{new Date(atual.data_fim).toLocaleDateString("pt-BR")}</strong>
            </div>
            <div>
              <p className="muted" style={{ margin: 0 }}>Valor</p>
              <strong>R$ {Number(atual.valor).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</strong>
            </div>
          </div>

          <div className="row mt-16">
            <Link to={`/contratos/${atual.id}`} className="btn btn-secondary">VISUALIZAR CONTRATO</Link>

            {atual.status === "proximo_vencimento" && (
              <button className="btn btn-primary" onClick={iniciarRenovacao} disabled={starting}>
                {starting ? "Iniciando..." : "INICIAR RENOVAÇÃO"}
              </button>
            )}
            {["em_renovacao", "aguardando_assinatura_cliente", "aguardando_assinatura_empresa"].includes(atual.status) && (
              <button className="btn btn-primary" onClick={iniciarRenovacao} disabled={starting}>
                Continuar renovação
              </button>
            )}
          </div>

          {atual.status === "proximo_vencimento" && atual.dias_para_vencer !== undefined && (
            <p className="muted mt-16">Seu contrato está próximo do vencimento. Vence em {atual.dias_para_vencer} dias.</p>
          )}
        </div>
      ) : (
        <p className="muted mt-16">Nenhum contrato ativo no momento.</p>
      )}

      <div className="row-between mt-32">
        <h3 style={{ margin: 0 }}>Meus contratos</h3>
        <Link to="/historico" className="muted">Ver histórico completo</Link>
      </div>
    </Layout>
  );
}
