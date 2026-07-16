import { useState } from "react";
import GraficoComparativo from "./GraficoComparativo";
import { simulacaoApi } from "../../services/api";
import { formatarAOA, formatarPct, formatarData } from "../../utils/formatadores";

export default function ResultadoSimulacao({ resultado }) {
  const [aExportar, setAExportar] = useState(false);
  const [erroExportar, setErroExportar] = useState("");

  if (!resultado) return null;

  const positivoReal = Number(resultado.rentabilidade_real_pct) >= 0;

  const exportarPdf = async () => {
    setErroExportar("");
    setAExportar(true);
    try {
      await simulacaoApi.relatorio(resultado.id, `simulacao_${resultado.ativo.ticker}_${resultado.id}.pdf`);
    } catch (e) {
      setErroExportar(e.message || "Não foi possível gerar o relatório.");
    } finally {
      setAExportar(false);
    }
  };

  return (
    <div className="painel p-6 space-y-6">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className="font-display font-semibold text-marfim-50">Resultado da simulação</h2>
          <p className="text-xs text-marfim-400 mt-1">
            {resultado.ativo.ticker} · {formatarData(resultado.data_inicio)} → {formatarData(resultado.data_fim)}
          </p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className={`text-xs font-medium px-3 py-1.5 rounded-full ${positivoReal ? "badge-ativo" : "badge-bloqueado"}`}>
            {positivoReal ? "Ganho real estimado" : "Perda real estimada"}
          </span>
          <button onClick={exportarPdf} disabled={aExportar} className="btn-secundario text-xs py-1.5 px-3">
            {aExportar ? "A gerar..." : "Exportar PDF"}
          </button>
        </div>
      </div>

      {erroExportar && <div className="text-xs bg-perigo-bg text-perigo rounded-[6px] px-3 py-2">{erroExportar}</div>}

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
        <div>
          <p className="text-xs text-marfim-400">Valor investido</p>
          <p className="numero font-semibold text-marfim-50 mt-1">{formatarAOA(resultado.valor_investido)}</p>
        </div>
        <div>
          <p className="text-xs text-marfim-400">Inflação acumulada</p>
          <p className="numero font-semibold text-marfim-50 mt-1">{formatarPct(resultado.inflacao_acumulada_pct)}</p>
        </div>
        <div>
          <p className="text-xs text-marfim-400">Valor final (nominal)</p>
          <p className="numero font-semibold text-marfim-50 mt-1">{formatarAOA(resultado.valor_final_nominal)}</p>
        </div>
        <div>
          <p className="text-xs text-marfim-400">Valor final (real)</p>
          <p className="numero font-semibold text-marfim-50 mt-1">{formatarAOA(resultado.valor_final_real)}</p>
        </div>
      </div>

      <GraficoComparativo nominalPct={resultado.rentabilidade_nominal_pct} realPct={resultado.rentabilidade_real_pct} />

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm border-t border-white/5 pt-4">
        <div>
          <p className="text-xs text-marfim-400">Rentabilidade nominal</p>
          <p className={`numero text-lg font-semibold mt-1 ${Number(resultado.rentabilidade_nominal_pct) >= 0 ? "text-sucesso" : "text-perigo"}`}>
            {formatarPct(resultado.rentabilidade_nominal_pct)}
          </p>
        </div>
        <div>
          <p className="text-xs text-marfim-400">Rentabilidade real (ajustada à inflação)</p>
          <p className={`numero text-lg font-semibold mt-1 ${positivoReal ? "text-sucesso" : "text-perigo"}`}>
            {formatarPct(resultado.rentabilidade_real_pct)}
          </p>
        </div>
      </div>

      <p className="text-[11px] text-marfim-400 border-t border-white/5 pt-4">
        Resultado meramente informativo e educacional — não constitui recomendação de investimento.
      </p>
    </div>
  );
}
