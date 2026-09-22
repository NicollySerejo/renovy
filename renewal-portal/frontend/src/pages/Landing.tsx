import { Link } from "react-router-dom";
import Layout from "../components/Layout";
import ExpiryRing from "../components/ExpiryRing";

const FEATURES = [
  { title: "Como funciona", text: "Você recebe um link, acessa seus dados e conclui a renovação em poucos passos, sem precisar trocar e-mails ou mensagens." },
  { title: "Segurança", text: "Seus dados ficam protegidos com autenticação segura e cada responsável só visualiza suas próprias informações." },
  { title: "Documentos digitais", text: "Envie seus documentos direto do celular ou computador, sem impressão e sem filas." },
  { title: "Renovação online", text: "Acompanhe o vencimento do seu contrato e renove por aditivo ou de forma completa, quando necessário." },
];

export default function Landing() {
  return (
    <Layout>
      <section className="row" style={{ alignItems: "center", gap: 48, flexWrap: "wrap", padding: "24px 0 56px" }}>
        <div style={{ flex: "1 1 420px" }}>
          <h1 style={{ fontSize: "2.6rem", maxWidth: 560 }}>
            Renove seu contrato de forma simples e segura.
          </h1>
          <p style={{ fontSize: "1.05rem", maxWidth: 480 }}>
            Tenha acesso ao seu contrato, documentos e processo de renovação em um único lugar.
          </p>
          <div className="row mt-16">
            <Link to="/login" className="btn btn-primary">ACESSAR MINHA CONTA</Link>
            <Link to="/primeiro-acesso" className="btn btn-secondary">Primeiro acesso</Link>
          </div>
        </div>
        <div className="card" style={{ flex: "1 1 320px", maxWidth: 380 }}>
          <div className="row-between">
            <div>
              <p className="muted" style={{ marginBottom: 4 }}>Contrato CT-1000-2025</p>
              <h3 style={{ margin: 0 }}>João da Silva</h3>
            </div>
            <ExpiryRing days={20} />
          </div>
          <p className="muted mt-16">
            Seu contrato vence em 20 dias. Continue vendo o contrato como está, ou inicie a renovação quando quiser.
          </p>
          <Link to="/login" className="btn btn-primary btn-block mt-16">Iniciar renovação</Link>
        </div>
      </section>

      <section className="grid-2" style={{ gridTemplateColumns: "repeat(2, 1fr)" }}>
        {FEATURES.map((f) => (
          <div key={f.title} className="card card-sm">
            <h3 style={{ fontSize: "1.1rem" }}>{f.title}</h3>
            <p style={{ margin: 0 }}>{f.text}</p>
          </div>
        ))}
      </section>
    </Layout>
  );
}
