export function formatarAOA(valor) {
  const n = Number(valor ?? 0);
  return new Intl.NumberFormat("pt-AO", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n) + " Kz";
}

export function formatarPct(valor, casas = 2) {
  const n = Number(valor ?? 0);
  const sinal = n > 0 ? "+" : "";
  return `${sinal}${n.toFixed(casas)}%`;
}

export function formatarData(valor) {
  if (!valor) return "—";
  return new Date(valor).toLocaleDateString("pt-PT", { year: "numeric", month: "short", day: "2-digit" });
}

export function formatarDataHora(valor) {
  if (!valor) return "—";
  return new Date(valor).toLocaleString("pt-PT", { year: "numeric", month: "short", day: "2-digit", hour: "2-digit", minute: "2-digit" });
}
