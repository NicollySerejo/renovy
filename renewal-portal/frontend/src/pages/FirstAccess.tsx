import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { AuthAPI } from "../api/client";
import { useAuth } from "../context/AuthContext";

type Stage = "identify" | "register";

export default function FirstAccess() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [stage, setStage] = useState<Stage>("identify");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [cpf, setCpf] = useState("");
  const [nomeCompleto, setNomeCompleto] = useState("");
  const [nomePaciente, setNomePaciente] = useState("");

  const [email, setEmail] = useState("");
  const [telefone, setTelefone] = useState("");
  const [senha, setSenha] = useState("");
  const [confirmarSenha, setConfirmarSenha] = useState("");

  async function handleIdentify(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await AuthAPI.identify({ cpf, nome_completo: nomeCompleto, nome_paciente: nomePaciente });
      if (!res.encontrado) {
        setError(res.mensagem);
      } else if (!res.primeiro_acesso) {
        setError(res.mensagem + " Redirecionando para o login...");
        setTimeout(() => navigate("/login"), 1500);
      } else {
        setStage("register");
      }
    } catch {
      setError("Não foi possível verificar seus dados agora. Tente novamente.");
    } finally {
      setLoading(false);
    }
  }

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (senha !== confirmarSenha) {
      setError("As senhas não conferem.");
      return;
    }
    setLoading(true);
    try {
      const res = await AuthAPI.register({ cpf, email, telefone, senha, confirmar_senha: confirmarSenha });
      login({ token: res.access_token, role: res.role, nome: res.nome });
      navigate("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Não foi possível concluir o cadastro.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Layout>
      <div className="card" style={{ maxWidth: 440, margin: "40px auto" }}>
        {stage === "identify" ? (
          <>
            <h2>Identifique seu cadastro</h2>
            <p className="muted">Informe os dados exatamente como estão no seu contrato.</p>
            <form onSubmit={handleIdentify} className="mt-16">
              <div className="field">
                <label htmlFor="cpf">CPF</label>
                <input id="cpf" value={cpf} onChange={(e) => setCpf(e.target.value)} placeholder="000.000.000-00" required />
              </div>
              <div className="field">
                <label htmlFor="nome">Nome completo</label>
                <input id="nome" value={nomeCompleto} onChange={(e) => setNomeCompleto(e.target.value)} required />
              </div>
              <div className="field">
                <label htmlFor="paciente">Nome do paciente</label>
                <input id="paciente" value={nomePaciente} onChange={(e) => setNomePaciente(e.target.value)} required />
              </div>
              {error && <p className="field-error">{error}</p>}
              <button className="btn btn-primary btn-block" disabled={loading}>
                {loading ? "Verificando..." : "CONTINUAR"}
              </button>
            </form>
          </>
        ) : (
          <>
            <h2>Complete seu acesso</h2>
            <p className="muted">Cadastro encontrado! Defina como você vai entrar no portal a partir de agora.</p>
            <form onSubmit={handleRegister} className="mt-16">
              <div className="field">
                <label htmlFor="email">E-mail</label>
                <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
              </div>
              <div className="field">
                <label htmlFor="telefone">Telefone</label>
                <input id="telefone" value={telefone} onChange={(e) => setTelefone(e.target.value)} required />
              </div>
              <div className="field">
                <label htmlFor="senha">Criar senha</label>
                <input id="senha" type="password" minLength={8} value={senha} onChange={(e) => setSenha(e.target.value)} required />
              </div>
              <div className="field">
                <label htmlFor="confirmar">Confirmar senha</label>
                <input id="confirmar" type="password" minLength={8} value={confirmarSenha} onChange={(e) => setConfirmarSenha(e.target.value)} required />
              </div>
              {error && <p className="field-error">{error}</p>}
              <button className="btn btn-primary btn-block" disabled={loading}>
                {loading ? "Criando acesso..." : "Criar acesso"}
              </button>
            </form>
          </>
        )}
      </div>
    </Layout>
  );
}
