const LABELS: Record<string, string> = {
  vigente: "Vigente",
  proximo_vencimento: "Próximo do vencimento",
  em_renovacao: "Em renovação",
  aguardando_assinatura_cliente: "Aguardando sua assinatura",
  aguardando_assinatura_empresa: "Aguardando a empresa",
  renovado: "Renovado",
  vencido: "Vencido",
  cancelado: "Cancelado",
};

export default function StatusBadge({ status }: { status: string }) {
  return <span className={`badge badge-${status}`}>{LABELS[status] || status}</span>;
}
