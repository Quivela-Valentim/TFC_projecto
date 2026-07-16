import { formatarAOA, formatarPct, formatarData } from "../../utils/formatadores";

export default function ComparacaoSimulacoes({ simulacoes, onFechar }) {
  if (!simulacoes || simulacoes.length === 0) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
      <div className="painel w-full max-w-3xl p-6 max-h-[85vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-display font-semibold text-lg text-marfim-50">Comparação de cenários</h3>
          <button onClick={onFechar} className="text-marfim-400 hover:text-marfim-50 text-sm">Fechar ✕</button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm min-w-[560px]">
            <thead>
              <tr className="border-b border-white/5 text-left text-xs text-marfim-400 uppercase tracking-wide">
                <th className="py-2.5 pr-4 font-medium">Critério</th>
                {simulacoes.map((s) => (
                  <th key={s.id} className="py-2.5 pr-4 font-medium text-right">{s.ativo.ticker}</th>
                ))}
              </tr>
            </thead>
            <tbody className="text-marfim-200">
              <Linha rotulo="Período" valores={simulacoes.map((s) => `${formatarData(s.data_inicio)} → ${formatarData(s.data_fim)}`)} />
              <Linha rotulo="Valor investido" valores={simulacoes.map((s) => formatarAOA(s.valor_investido))} />
              <Linha rotulo="Inflação acumulada" valores={simulacoes.map((s) => formatarPct(s.inflacao_acumulada_pct))} />
              <Linha
                rotulo="Rentabilidade nominal"
                valores={simulacoes.map((s) => formatarPct(s.rentabilidade_nominal_pct))}
                cores={simulacoes.map((s) => (Number(s.rentabilidade_nominal_pct) >= 0 ? "text-sucesso" : "text-perigo"))}
              />
              <Linha
                rotulo="Rentabilidade real"
                valores={simulacoes.map((s) => formatarPct(s.rentabilidade_real_pct))}
                cores={simulacoes.map((s) => (Number(s.rentabilidade_real_pct) >= 0 ? "text-sucesso" : "text-perigo"))}
              />
              <Linha rotulo="Valor final (real)" valores={simulacoes.map((s) => formatarAOA(s.valor_final_real))} />
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function Linha({ rotulo, valores, cores }) {
  return (
    <tr className="border-b border-white/5 last:border-0">
      <td className="py-2.5 pr-4 text-marfim-400">{rotulo}</td>
      {valores.map((v, i) => (
        <td key={i} className={`py-2.5 pr-4 text-right numero font-medium ${cores?.[i] || ""}`}>{v}</td>
      ))}
    </tr>
  );
}
