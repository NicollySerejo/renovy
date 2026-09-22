import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { AuthAPI } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [identificador, setIdentificador] = useState("");
  const [senha, setSenha] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await AuthAPI.login({ identificador, senha });
      login({ token: res.access_token, role: res.role, nome: res.nome });
      navigate(res.role === "cliente" ? "/dashboard" : "/admin");
    } catch {
      setError("CPF/e-mail ou senha inválidos.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Layout>
      <div className="card" style={{ maxWidth: 400, margin: "40px auto" }}>
        <h2>Entrar</h2>
        <p className="muted">Acesse com seu CPF ou e-mail cadastrado.</p>
        <form onSubmit={handleSubmit} className="mt-16">
          <div className="field">
            <label htmlFor="identificador">CPF ou e-mail</label>
            <input id="identificador" value={identificador} onChange={(e) => setIdentificador(e.target.value)} required />
          </div>
          <div className="field">
            <label htmlFor="senha">Senha</label>
            <input id="senha" type="password" value={senha} onChange={(e) => setSenha(e.target.value)} required />
          </div>
          {error && <p className="field-error">{error}</p>}
          <button className="btn btn-primary btn-block" disabled={loading}>
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>
        <div className="row-between mt-16">
          <Link to="/primeiro-acesso" className="muted">Esqueci minha senha</Link>
          <Link to="/primeiro-acesso" className="muted">Primeiro acesso</Link>
        </div>
      </div>
    </Layout>
  );
}
