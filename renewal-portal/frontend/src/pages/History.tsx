import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Layout from "../components/Layout";
import StatusBadge from "../components/StatusBadge";
import { ContractAPI, Contract } from "../api/client";

export default function History() {
  const [contracts, setContracts] = useState<Contract[]>([]);

  useEffect(() => {
    ContractAPI.list().then((list) =>
      setContracts([...list].sort((a, b) => new Date(b.data_inicio).getTime() - new Date(a.data_inicio).getTime()))
    );
  }, []);

  return (
    <Layout>
      <h2>Meus contratos</h2>
      <p className="muted">Contratos antigos não são sobrescritos — cada renovação gera um novo registro.</p>

      <div className="stack mt-16">
        {contracts.map((c) => (
          <Link to={`/contratos/${c.id}`} key={c.id} className="card card-sm row-between" style={{ textDecoration: "none", color: "inherit" }}>
            <div>
              <p className="muted" style={{ margin: 0 }}>{new Date(c.data_inicio).getFullYear()}</p>
              <strong>Contrato {c.numero}</strong>
              <p className="muted" style={{ margin: "2px 0 0" }}>
                {new Date(c.data_inicio).toLocaleDateString("pt-BR")} até {new Date(c.data_fim).toLocaleDateString("pt-BR")}
              </p>
            </div>
            <StatusBadge status={c.status} />
          </Link>
        ))}
        {contracts.length === 0 && <p className="muted">Nenhum contrato encontrado.</p>}
      </div>
    </Layout>
  );
}
