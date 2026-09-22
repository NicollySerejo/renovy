import { useState } from "react";
import { Contract, Renewal, RenewalAPI } from "../../api/client";

export default function RenewalAditivo({
  contract,
  renewal,
  onSubmitted,
}: {
  contract: Contract;
  renewal: Renewal;
  onSubmitted: () => void;
}) {
  const dadosSalvos = renewal.dados_json ? JSON.parse(renewal.dados_json) : {};
  const [novoValor, setNovoValor] = useState<string>(dadosSalvos.novo_valor ?? contract.valor.toString());
  const [novaInicio, setNovaInicio] = useState<string>(dadosSalvos.nova_data_inicio ?? contract.data_fim);
  const [novaFim, setNovaFim] = useState<string>(dadosSalvos.nova_data_fim ?? "");
  const [saving, setSaving] = useState(false);
  const [confirmando, setConfirmando] = useState(false);

  async function handleConfirmar() {
    setSaving(true);
    try {
      await RenewalAPI.updateAditivo(renewal.id, {
        novo_valor: parseFloat(novoValor),
        nova_data_inicio: novaInicio,
        nova_data_fim: novaFim,
      });
      await RenewalAPI.submit(renewal.id);
      onSubmitted();
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="card">
      <h2>Renovação por aditivo</h2>
      <p className="muted">Altere somente os dados que mudaram. O restante do contrato permanece igual.</p>

      <div className="grid-2 mt-32">
        <div>
          <h3 style={{ fontSize: "1rem" }}>Dados atuais</h3>
          <p className="muted" style={{ margin: 0 }}>Valor</p>
          <strong>R$ {Number(contract.valor).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</strong>
          <p className="muted mt-16" style={{ marginBottom: 0 }}>Vigência</p>
          <strong>
            {new Date(contract.data_inicio).toLocaleDateString("pt-BR")} até {new Date(contract.data_fim).toLocaleDateString("pt-BR")}
          </strong>
        </div>

        <div>
          <h3 style={{ fontSize: "1rem" }}>Nova vigência e valor</h3>
          <div className="field">
            <label>Novo valor (R$)</label>
            <input type="number" step="0.01" value={novoValor} onChange={(e) => setNovoValor(e.target.value)} />
          </div>
          <div className="field">
            <label>Início da nova vigência</label>
            <input type="date" value={novaInicio} onChange={(e) => setNovaInicio(e.target.value)} />
          </div>
          <div className="field">
            <label>Fim da nova vigência</label>
            <input type="date" value={novaFim} onChange={(e) => setNovaFim(e.target.value)} required />
          </div>
        </div>
      </div>

      {!confirmando ? (
        <button className="btn btn-primary mt-16" onClick={() => setConfirmando(true)} disabled={!novaFim}>
          Continuar
        </button>
      ) : (
        <div className="card card-sm mt-16" style={{ background: "var(--surface-sunken)" }}>
          <p style={{ margin: 0 }}>Confira todas as informações antes de continuar.</p>
          <div className="row mt-16">
            <button className="btn btn-ghost" onClick={() => setConfirmando(false)}>Voltar e editar</button>
            <button className="btn btn-primary" onClick={handleConfirmar} disabled={saving}>
              {saving ? "Enviando..." : "CONFIRMAR RENOVAÇÃO"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
