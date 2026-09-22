import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { AdminAPI } from "../api/client";

const initial = {
  nome: "",
  cpf: "",
  email: "",
  telefone: "",
  paciente_nome: "",
  paciente_data_nascimento: "",
  contrato_numero: "",
  contrato_valor: "",
  contrato_data_inicio: "",
  contrato_data_fim: "",
  contrato_condicoes: "",
  tipo_proxima_renovacao: "aditivo",
};

export default function AdminClientNew() {
  const navigate = useNavigate();
  const [form, setForm] = useState(initial);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  function set<K extends keyof typeof initial>(key: K, value: string) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      await AdminAPI.createClient({
        ...form,
        contrato_valor: parseFloat(form.contrato_valor),
      });
      navigate("/admin");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Não foi possível cadastrar o cliente.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Layout>
      <h2>Cadastrar cliente</h2>
      <p className="muted">Cadastra o responsável, o paciente vinculado e o contrato inicial.</p>

      <form onSubmit={handleSubmit} className="card mt-16">
        <h3 style={{ fontSize: "1rem" }}>Responsável</h3>
        <div className="grid-2">
          <Field label="Nome completo" value={form.nome} onChange={(v) => set("nome", v)} required />
          <Field label="CPF" value={form.cpf} onChange={(v) => set("cpf", v)} required />
          <Field label="E-mail" type="email" value={form.email} onChange={(v) => set("email", v)} required />
          <Field label="Telefone" value={form.telefone} onChange={(v) => set("telefone", v)} required />
        </div>

        <h3 style={{ fontSize: "1rem" }} className="mt-16">Paciente</h3>
        <div className="grid-2">
          <Field label="Nome do paciente" value={form.paciente_nome} onChange={(v) => set("paciente_nome", v)} required />
          <Field label="Data de nascimento" type="date" value={form.paciente_data_nascimento} onChange={(v) => set("paciente_data_nascimento", v)} />
        </div>

        <h3 style={{ fontSize: "1rem" }} className="mt-16">Contrato inicial</h3>
        <div className="grid-2">
          <Field label="Número do contrato" value={form.contrato_numero} onChange={(v) => set("contrato_numero", v)} required />
          <Field label="Valor (R$)" type="number" value={form.contrato_valor} onChange={(v) => set("contrato_valor", v)} required />
          <Field label="Início" type="date" value={form.contrato_data_inicio} onChange={(v) => set("contrato_data_inicio", v)} required />
          <Field label="Término" type="date" value={form.contrato_data_fim} onChange={(v) => set("contrato_data_fim", v)} required />
          <Field label="Condições" value={form.contrato_condicoes} onChange={(v) => set("contrato_condicoes", v)} />
          <div className="field">
            <label>Tipo da próxima renovação</label>
            <select value={form.tipo_proxima_renovacao} onChange={(e) => set("tipo_proxima_renovacao", e.target.value)}>
              <option value="aditivo">Aditivo</option>
              <option value="completa">Renovação completa</option>
            </select>
          </div>
        </div>

        {error && <p className="field-error">{error}</p>}
        <button className="btn btn-primary mt-16" disabled={saving}>
          {saving ? "Cadastrando..." : "Cadastrar cliente"}
        </button>
      </form>
    </Layout>
  );
}

function Field({
  label,
  value,
  onChange,
  type = "text",
  required = false,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  required?: boolean;
}) {
  return (
    <div className="field">
      <label>{label}</label>
      <input type={type} value={value} onChange={(e) => onChange(e.target.value)} required={required} />
    </div>
  );
}
