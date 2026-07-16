import { useState } from "react";
import { simulacaoApi } from "../../services/api";
import { formatarAOA, formatarPct, formatarData } from "../../utils/formatadores";

export default function HistoricoSimulacoes({ simulacoes, onComparar }) {
  const [selecionadas, setSelecionadas] = useState([]);
  const [aExportarId, setAExportarId] = useState(null);

  const alternar = (id) => {
    setSelecionadas((atual) => (atual.includes(id) ? atual.filter((x) => x !== id) : [...atual, id]));
  };

  const exportar = async (s) => {
    setAExportarId(s.id);
    try {
      await simulacaoApi.relatorio(s.id, `simulacao_${s.ativo.ticker}_${s.id}.pdf`);
    } finally {
      setAExportarId(null);
    }
  };

  if (!simulacoes || simulacoes.length === 0) {
    return <div className="painel p-6 text-sm text-marfim-300">Ainda não tem simulações guardadas.</div>;
  }

  return (
    <div className="painel overflow-hidden">
      <div className="flex items-center justify-between px-5 py-4 border-b border-white/5">
        <h2 className="font-display font-semibold text-marfim-50">Histórico de simulações</h2>
        <button
          className="btn-secundario text-xs py-1.5 px-3 disabled:opacity-40"
          disabled={selecionadas.length < 2}
          onClick={() => onComparar(selecionadas)}
        >
          Comparar seleccionadas ({selecionadas.length})
        </button>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/5 text-left text-xs text-marfim-400 uppercase tracking-wide">
            <th className="px-5 py-3 font-medium w-8" />
            <th className="px-5 py-3 font-medium">Ativo</th>
            <th className="px-5 py-3 font-medium text-right">Período</th>
            <th className="px-5 py-3 font-medium text-right">Investido</th>
            <th className="px-5 py-3 font-medium text-right">Nominal</th>
            <th className="px-5 py-3 font-medium text-right">Real</th>
            <th className="px-5 py-3 font-medium text-right">Relatório</th>
          </tr>
        </thead>
        <tbody>
          {simulacoes.map((s) => (
            <tr key={s.id} className="border-b border-white/5 last:border-0 hover:bg-white/[0.02]">
              <td className="px-5 py-3">
                <input type="checkbox" checked={selecionadas.includes(s.id)} onChange={() => alternar(s.id)} className="accent-vivo-500" />
              </td>
              <td className="px-5 py-3 font-medium text-marfim-50">{s.ativo.ticker}</td>
              <td className="px-5 py-3 text-right text-xs text-marfim-400">{formatarData(s.data_inicio)} → {formatarData(s.data_fim)}</td>
              <td className="px-5 py-3 text-right numero text-marfim-200">{formatarAOA(s.valor_investido)}</td>
              <td className={`px-5 py-3 text-right numero font-medium ${Number(s.rentabilidade_nominal_pct) >= 0 ? "text-sucesso" : "text-perigo"}`}>
                {formatarPct(s.rentabilidade_nominal_pct)}
              </td>
              <td className={`px-5 py-3 text-right numero font-medium ${Number(s.rentabilidade_real_pct) >= 0 ? "text-sucesso" : "text-perigo"}`}>
                {formatarPct(s.rentabilidade_real_pct)}
              </td>
              <td className="px-5 py-3 text-right">
                <button
                  onClick={() => exportar(s)}
                  disabled={aExportarId === s.id}
                  className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg
                             bg-vivo-500/15 text-vivo-400 hover:bg-vivo-500 hover:text-white
                             transition disabled:opacity-40"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5">
                    <path d="M12 3v12m0 0-4-4m4 4 4-4M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
                  </svg>
                  {aExportarId === s.id ? "A gerar..." : "PDF"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}