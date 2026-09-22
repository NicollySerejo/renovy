import { useState } from "react";
import { Contract, Renewal, RenewalAPI, DocumentAPI } from "../../api/client";

const STEPS = [
  { key: "responsavel", label: "Responsável" },
  { key: "paciente", label: "Paciente" },
  { key: "endereco", label: "Endereço" },
  { key: "contato", label: "Contato" },
  { key: "contratuais", label: "Contratuais" },
  { key: "documentos", label: "Documentos" },
  { key: "revisao", label: "Revisão" },
];

export default function RenewalCompleta({
  contract,
  renewal,
  onSubmitted,
}: {
  contract: Contract;
  renewal: Renewal;
  onSubmitted: () => void;
}) {
  const dadosSalvos = renewal.dados_json ? JSON.parse(renewal.dados_json) : {};
  const [stepIndex, setStepIndex] = useState(0);
  const [data, setData] = useState<Record<string, any>>({
    responsavel: dadosSalvos.responsavel ?? {},
    paciente: dadosSalvos.paciente ?? {},
    endereco: dadosSalvos.endereco ?? {},
    contato: dadosSalvos.contato ?? {},
    contratuais: dadosSalvos.contratuais ?? { valor: contract.valor, data_inicio: contract.data_fim, data_fim: "", condicoes: contract.condicoes },
    documentos: dadosSalvos.documentos ?? {},
  });
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadedNames, setUploadedNames] = useState<string[]>([]);

  const step = STEPS[stepIndex];

  function setField(section: string, field: string, value: any) {
    setData((prev) => ({ ...prev, [section]: { ...prev[section], [field]: value } }));
  }

  async function goNext() {
    setSaving(true);
    try {
      if (step.key !== "revisao" && step.key !== "documentos") {
        await RenewalAPI.updateEtapa(renewal.id, step.key, data[step.key]);
      }
      if (step.key === "contratuais") {
        await RenewalAPI.updateEtapa(renewal.id, "contratuais", data.contratuais);
      }
      if (stepIndex < STEPS.length - 1) setStepIndex(stepIndex + 1);
    } finally {
      setSaving(false);
    }
  }

  function goBack() {
    if (stepIndex > 0) setStepIndex(stepIndex - 1);
  }

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await DocumentAPI.upload(file, { tipo: "documento_renovacao", contract_id: contract.id, renewal_id: renewal.id });
      setUploadedNames((prev) => [...prev, file.name]);
    } finally {
      setUploading(false);
    }
  }

  async function handleConfirmar() {
    setSaving(true);
    try {
      await RenewalAPI.submit(renewal.id);
      onSubmitted();
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="card">
      <h2>Renovação completa</h2>
      <p className="muted">Revise e preencha novamente as informações necessárias para o novo contrato.</p>

      <div className="stepper mt-16">
        {STEPS.map((s, i) => (
          <span key={s.key} className={`step-pill ${i === stepIndex ? "active" : i < stepIndex ? "done" : ""}`}>
            {i + 1}. {s.label}
          </span>
        ))}
      </div>

      {step.key === "responsavel" && (
        <div className="grid-2">
          <TextField label="Nome completo" value={data.responsavel.nome ?? contract.cliente_nome ?? ""} onChange={(v) => setField("responsavel", "nome", v)} />
          <TextField label="CPF" value={data.responsavel.cpf ?? ""} onChange={(v) => setField("responsavel", "cpf", v)} />
        </div>
      )}

      {step.key === "paciente" && (
        <div className="grid-2">
          <TextField label="Nome do paciente" value={data.paciente.nome ?? contract.paciente_nome ?? ""} onChange={(v) => setField("paciente", "nome", v)} />
          <TextField label="Data de nascimento" type="date" value={data.paciente.data_nascimento ?? ""} onChange={(v) => setField("paciente", "data_nascimento", v)} />
        </div>
      )}

      {step.key === "endereco" && (
        <div className="grid-2">
          <TextField label="CEP" value={data.endereco.cep ?? ""} onChange={(v) => setField("endereco", "cep", v)} />
          <TextField label="Endereço" value={data.endereco.logradouro ?? ""} onChange={(v) => setField("endereco", "logradouro", v)} />
          <TextField label="Número" value={data.endereco.numero ?? ""} onChange={(v) => setField("endereco", "numero", v)} />
          <TextField label="Cidade / UF" value={data.endereco.cidade ?? ""} onChange={(v) => setField("endereco", "cidade", v)} />
        </div>
      )}

      {step.key === "contato" && (
        <div className="grid-2">
          <TextField label="E-mail" value={data.contato.email ?? ""} onChange={(v) => setField("contato", "email", v)} />
          <TextField label="Telefone" value={data.contato.telefone ?? ""} onChange={(v) => setField("contato", "telefone", v)} />
        </div>
      )}

      {step.key === "contratuais" && (
        <div className="grid-2">
          <TextField label="Valor (R$)" type="number" value={data.contratuais.valor ?? ""} onChange={(v) => setField("contratuais", "valor", parseFloat(v))} />
          <TextField label="Início" type="date" value={data.contratuais.data_inicio ?? ""} onChange={(v) => setField("contratuais", "data_inicio", v)} />
          <TextField label="Término" type="date" value={data.contratuais.data_fim ?? ""} onChange={(v) => setField("contratuais", "data_fim", v)} />
          <TextField label="Condições" value={data.contratuais.condicoes ?? ""} onChange={(v) => setField("contratuais", "condicoes", v)} />
        </div>
      )}

      {step.key === "documentos" && (
        <div>
          <div className="field">
            <label>Enviar documento (PDF ou imagem)</label>
            <input type="file" accept=".pdf,.jpg,.jpeg,.png,.webp" onChange={handleUpload} disabled={uploading} />
          </div>
          {uploadedNames.length > 0 && (
            <ul className="muted">
              {uploadedNames.map((n) => <li key={n}>{n}</li>)}
            </ul>
          )}
        </div>
      )}

      {step.key === "revisao" && (
        <div className="stack">
          <p><strong>Responsável:</strong> {data.responsavel.nome} — CPF {data.responsavel.cpf}</p>
          <p><strong>Paciente:</strong> {data.paciente.nome}</p>
          <p><strong>Endereço:</strong> {data.endereco.logradouro}, {data.endereco.numero} — {data.endereco.cidade}</p>
          <p><strong>Contato:</strong> {data.contato.email} / {data.contato.telefone}</p>
          <p><strong>Valor:</strong> R$ {data.contratuais.valor} | <strong>Vigência:</strong> {data.contratuais.data_inicio} até {data.contratuais.data_fim}</p>
          <p><strong>Documentos enviados:</strong> {uploadedNames.length}</p>
          <div className="card card-sm" style={{ background: "var(--surface-sunken)" }}>
            Confira todas as informações antes de continuar.
          </div>
        </div>
      )}

      <div className="row mt-32">
        {stepIndex > 0 && <button className="btn btn-ghost" onClick={goBack}>Voltar</button>}
        {step.key !== "revisao" ? (
          <button className="btn btn-primary" onClick={goNext} disabled={saving}>
            {saving ? "Salvando..." : "Próxima etapa"}
          </button>
        ) : (
          <button className="btn btn-primary" onClick={handleConfirmar} disabled={saving}>
            {saving ? "Enviando..." : "CONFIRMAR RENOVAÇÃO"}
          </button>
        )}
      </div>
    </div>
  );
}

function TextField({
  label,
  value,
  onChange,
  type = "text",
}: {
  label: string;
  value: any;
  onChange: (v: string) => void;
  type?: string;
}) {
  return (
    <div className="field">
      <label>{label}</label>
      <input type={type} value={value} onChange={(e) => onChange(e.target.value)} />
    </div>
  );
}
