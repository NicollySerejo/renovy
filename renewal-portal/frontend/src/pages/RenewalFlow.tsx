import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import RenewalAditivo from "./renewal/RenewalAditivo";
import RenewalCompleta from "./renewal/RenewalCompleta";
import SignatureStep from "./renewal/SignatureStep";
import { useAuth } from "../context/AuthContext";
import { RenewalAPI, ContractAPI, Renewal, Contract } from "../api/client";

export default function RenewalFlow() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { session } = useAuth();
  const [renewal, setRenewal] = useState<Renewal | null>(null);
  const [contract, setContract] = useState<Contract | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    if (!id) return;
    const r = await RenewalAPI.get(id);
    setRenewal(r);
    const c = await ContractAPI.get(r.contract_id);
    setContract(c);
    setLoading(false);
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  if (loading || !renewal || !contract) return <Layout><p className="muted">Carregando...</p></Layout>;

  const isStaff = session?.role === "funcionario" || session?.role === "administrador";

  return (
    <Layout>
      <h2>Renovação — Contrato {contract.numero}</h2>

      {renewal.status === "em_preenchimento" && renewal.tipo === "aditivo" && (
        <RenewalAditivo contract={contract} renewal={renewal} onSubmitted={load} />
      )}

      {renewal.status === "em_preenchimento" && renewal.tipo === "completa" && (
        <RenewalCompleta contract={contract} renewal={renewal} onSubmitted={load} />
      )}

      {renewal.status === "aguardando_assinatura_cliente" && !isStaff && (
        <SignatureStep renewal={renewal} tipo="cliente" onSigned={load} />
      )}
      {renewal.status === "aguardando_assinatura_cliente" && isStaff && (
        <div className="card"><p className="muted" style={{ margin: 0 }}>Aguardando a assinatura do responsável pelo contrato.</p></div>
      )}

      {renewal.status === "aguardando_assinatura_empresa" && isStaff && (
        <SignatureStep renewal={renewal} tipo="empresa" onSigned={load} />
      )}
      {renewal.status === "aguardando_assinatura_empresa" && !isStaff && (
        <div className="card"><p className="muted" style={{ margin: 0 }}>Sua assinatura foi registrada. Aguardando a confirmação da empresa.</p></div>
      )}

      {renewal.status === "concluida" && (
        <div className="card center">
          <h3>Renovação concluída!</h3>
          <p className="muted">Seu novo contrato já está disponível.</p>
          <button className="btn btn-primary mt-16" onClick={() => navigate(isStaff ? "/admin" : "/dashboard")}>
            {isStaff ? "Voltar ao painel" : "Ir para minha área"}
          </button>
        </div>
      )}
    </Layout>
  );
}
