import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { dashboardApi } from "../services/api";
import CabecalhoPagina from "../components/shared/CabecalhoPagina";
import CardIndicador from "../components/dashboard/CardIndicador";
import { formatarAOA, formatarPct, formatarData } from "../utils/formatadores";

export default function DashboardPage() {
  const [dados, setDados] = useState(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    dashboardApi
      .investidor()
      .then(setDados)
      .catch((e) => setErro(e.message));
  }, []);

  if (erro) {
    return (
      <div className="px-8 py-6">
        <div className="text-sm bg-perigo-bg text-perigo rounded-[6px] px-4 py-3">{erro}</div>
      </div>
    );
  }

  if (!dados) {
    return (
      <div className="h-64 flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-vivo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div>
      <CabecalhoPagina
        titulo="Dashboard"
        subtitulo="Resumo da sua carteira fictícia e das simulações realizadas."
        acoes={
          <Link to="/simulacao" className="btn-primario text-sm">
            Nova simulação
          </Link>
        }
      />

      <div className="p-4 sm:p-8 space-y-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <CardIndicador rotulo="Total investido" valor={formatarAOA(dados.carteira.valor_investido)} />
          <CardIndicador rotulo="Valor atual" valor={formatarAOA(dados.carteira.valor_atual)} variacao={dados.rentabilidade_nominal_geral_pct} destaque />
          <CardIndicador
            rotulo="Rentabilidade real geral"
            valor={dados.rentabilidade_real_geral_pct !== null ? formatarPct(dados.rentabilidade_real_geral_pct) : "—"}
          />
          <CardIndicador rotulo="Simulações realizadas" valor={dados.numero_simulacoes} />
        </div>

        {dados.posicoes_sem_inflacao_suficiente?.length > 0 && (
          <div className="text-xs bg-aviso-bg text-aviso rounded-[6px] px-4 py-3">
            A rentabilidade real geral não inclui {dados.posicoes_sem_inflacao_suficiente.join(", ")} por
            faltarem dados de inflação para o respetivo período. Peça ao administrador para completar o histórico.
          </div>
        )}

        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-display font-semibold text-marfim-50">Últimas simulações</h2>
            <Link to="/simulacao" className="text-xs text-vivo-400 hover:text-vivo-300">Ver todas</Link>
          </div>

          {dados.ultimas_simulacoes.length === 0 ? (
            <div className="painel p-8 text-center text-sm text-marfim-300">
              Ainda não realizou nenhuma simulação. <Link to="/simulacao" className="text-vivo-400 hover:underline">Simular agora</Link>.
            </div>
          ) : (
            <div className="painel overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/5 text-left text-xs text-marfim-400 uppercase tracking-wide">
                    <th className="px-5 py-3 font-medium">Ativo</th>
                    <th className="px-5 py-3 font-medium text-right">Período</th>
                    <th className="px-5 py-3 font-medium text-right">Valor investido</th>
                    <th className="px-5 py-3 font-medium text-right">Rent. nominal</th>
                    <th className="px-5 py-3 font-medium text-right">Rent. real</th>
                    <th className="px-5 py-3 font-medium text-right">Data</th>
                  </tr>
                </thead>
                <tbody>
                  {dados.ultimas_simulacoes.map((s) => (
                    <tr key={s.id} className="border-b border-white/5 last:border-0">
                      <td className="px-5 py-3 font-medium text-marfim-50">{s.ativo.ticker}</td>
                      <td className="px-5 py-3 text-right text-xs text-marfim-400">{formatarData(s.data_inicio)} → {formatarData(s.data_fim)}</td>
                      <td className="px-5 py-3 text-right numero text-marfim-200">{formatarAOA(s.valor_investido)}</td>
                      <td className={`px-5 py-3 text-right numero font-medium ${Number(s.rentabilidade_nominal_pct) >= 0 ? "text-sucesso" : "text-perigo"}`}>
                        {formatarPct(s.rentabilidade_nominal_pct)}
                      </td>
                      <td className={`px-5 py-3 text-right numero font-medium ${Number(s.rentabilidade_real_pct) >= 0 ? "text-sucesso" : "text-perigo"}`}>
                        {formatarPct(s.rentabilidade_real_pct)}
                      </td>
                      <td className="px-5 py-3 text-right text-xs text-marfim-400">{formatarData(s.criada_em)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
