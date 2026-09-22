interface Props {
  days: number;
  totalWindow?: number; // janela de referencia para a proporcao do anel
}

/** Anel que mostra visualmente quantos dias faltam para o vencimento do
 * contrato. E o elemento visual recorrente do produto: aparece no card do
 * dashboard, na lista administrativa e no alerta de renovacao. */
export default function ExpiryRing({ days, totalWindow = 30 }: Props) {
  const clamped = Math.max(0, Math.min(days, totalWindow));
  const ratio = days < 0 ? 0 : clamped / totalWindow;
  const radius = 34;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - ratio);

  let tone = "";
  if (days < 0) tone = "danger";
  else if (days <= 7) tone = "danger";
  else if (days <= 30) tone = "warn";

  return (
    <div className={`expiry-ring ${tone}`} role="img" aria-label={`${days} dias para o vencimento`}>
      <svg width="84" height="84" viewBox="0 0 84 84">
        <circle className="track" cx="42" cy="42" r={radius} />
        <circle
          className="progress"
          cx="42"
          cy="42"
          r={radius}
          strokeDasharray={circumference}
          strokeDashoffset={days < 0 ? 0 : offset}
        />
      </svg>
      <div className="ring-label">
        <span className="ring-number">{days < 0 ? "0" : days}</span>
        <span className="ring-unit">{days < 0 ? "vencido" : "dias"}</span>
      </div>
    </div>
  );
}
