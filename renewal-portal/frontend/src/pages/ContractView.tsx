import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import Layout from "../components/Layout";
import StatusBadge from "../components/StatusBadge";
import { ContractAPI, Contract } from "../api/client";

export default function ContractView() {
  const { id } = useParams();
  const [contract, setContract] = useState<Contract | null>(null);

  useEffect(() => {
    if (id) ContractAPI.get(id).then(setContract);
  }, [id]);

  if (!contract) return <Layout><p className="muted">Carregando...</p></Layout>;

  return (
    <Layout>
      <Link to="/dashboard" className="muted">&larr; Voltar</Link>
      <div className="card mt-16">
        <div className="row-between">
          <div>
            <h2 style={{ margin: 0 }}>Contrato {contract.numero}</h2>
            <p className="muted" style={{ margin: "4px 0 0" }}>Documento histórico — não pode ser alterado diretamente.</p>
          </div>
          <StatusBadge status={contract.status} />
        </div>

        <div className="grid-2 mt-32">
          <Field label="Responsável" value={contract.cliente_nome} />
          <Field label="Paciente" value={contract.paciente_nome} />
          <Field label="Início" value={new Date(contract.data_inicio).toLocaleDateString("pt-BR")} />
          <Field label="Término" value={new Date(contract.data_fim).toLocaleDateString("pt-BR")} />
          <Field label="Valor" value={`R$ ${Number(contract.valor).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`} />
          <Field label="Condições" value={contract.condicoes || "-"} />
        </div>

        <div className="row mt-32">
          <a href={ContractAPI.documentUrl(contract.id)} target="_blank" rel="noreferrer" className="btn btn-secondary">
            VISUALIZAR PDF
          </a>
          <a href={ContractAPI.documentUrl(contract.id)} download className="btn btn-secondary">
            BAIXAR CONTRATO
          </a>
        </div>
      </div>
    </Layout>
  );
}

function Field({ label, value }: { label: string; value?: string | null }) {
  return (
    <div>
      <p className="muted" style={{ margin: 0 }}>{label}</p>
      <strong>{value ?? "-"}</strong>
    </div>
  );
}
