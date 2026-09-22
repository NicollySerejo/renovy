import { useState } from "react";
import { Renewal, SignatureAPI } from "../../api/client";
import { useAuth } from "../../context/AuthContext";

export default function SignatureStep({
  renewal,
  tipo,
  onSigned,
}: {
  renewal: Renewal;
  tipo: "cliente" | "empresa";
  onSigned: () => void;
}) {
  const { session } = useAuth();
  const [conferi, setConferi] = useState(false);
  const [nome, setNome] = useState(session?.nome ?? "");
  const [signing, setSigning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSign() {
    setError(null);
    setSigning(true);
    try {
      await SignatureAPI.sign({ renewal_id: renewal.id, tipo, nome_assinante: nome, confirmo_leitura: conferi });
      onSigned();
    } catch {
      setError("Não foi possível registrar a assinatura. Tente novamente.");
    } finally {
      setSigning(false);
    }
  }

  return (
    <div className="card">
      <h2>Assinatura</h2>
      <p className="muted">Leia as informações da renovação antes de assinar.</p>

      <div className="card card-sm mt-16" style={{ background: "var(--surface-sunken)" }}>
        <p style={{ margin: 0 }}>
          Ao assinar, você confirma que revisou e concorda com os dados informados nesta renovação
          ({tipo === "cliente" ? "assinatura do responsável" : "aprovação da empresa"}).
        </p>
      </div>

      <div className="field mt-16">
        <label>Nome de quem assina</label>
        <input value={nome} onChange={(e) => setNome(e.target.value)} />
      </div>

      <label className="row" style={{ alignItems: "flex-start", cursor: "pointer" }}>
        <input type="checkbox" checked={conferi} onChange={(e) => setConferi(e.target.checked)} style={{ marginTop: 4 }} />
        <span>Conferi todas as informações e concordo com os termos desta renovação.</span>
      </label>

      {error && <p className="field-error">{error}</p>}

      <button className="btn btn-primary mt-16" onClick={handleSign} disabled={!conferi || !nome || signing}>
        {signing ? "Assinando..." : "Assinar e confirmar"}
      </button>
    </div>
  );
}
