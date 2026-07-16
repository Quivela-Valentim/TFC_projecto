import { useEffect, useState } from "react";
import { dashboardApi } from "../../services/api";
import CabecalhoPagina from "../../components/shared/CabecalhoPagina";
import CardIndicador from "../../components/dashboard/CardIndicador";
import { formatarPct, formatarDataHora } from "../../utils/formatadores";

export default function AdminDashboardPage() {
  const [dados, setDados] = useState(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    dashboardApi.admin().then(setDados).catch((e) => setErro(e.message));
  }, []);

  if (erro) return <div className="p-4 sm:p-8 text-sm bg-perigo-bg text-perigo rounded-xl">{erro}</div>;
  if (!dados) return <div className="h-64 flex items-center justify-center"><div className="w-6 h-6 border-2 border-vivo-500 border-t-transparent rounded-full animate-spin" /></div>;

  return (
    <div>
      <CabecalhoPagina titulo="Dashboard do Administrador" subtitulo="Visão geral da utilização da plataforma." />

      <div className="p-4 sm:p-8 space-y-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <CardIndicador rotulo="Utilizadores registados" valor={dados.total_utilizadores} />
          <CardIndicador rotulo="Utilizadores ativos" valor={dados.utilizadores_ativos} />
          <CardIndicador rotulo="Utilizadores bloqueados" valor={dados.utilizadores_bloqueados} />
          <CardIndicador rotulo="Total de simulações" valor={dados.total_simulacoes} />
        </div>

        {dados.tentativas_login_falhadas_recentes > 0 && (
          <div className="text-sm bg-aviso-bg text-aviso rounded-xl px-4 py-3">
            {dados.tentativas_login_falhadas_recentes} tentativa(s) de login falhada(s) nas últimas 24 horas.
          </div>
        )}

        <div>
          <h2 className="font-display font-semibold text-marfim-50 mb-3">Simulações recentes</h2>
          {dados.simulacoes_recentes.length === 0 ? (
            <div className="painel p-8 text-center text-sm text-marfim-300">Ainda não existem simulações no sistema.</div>
          ) : (
            <div className="painel overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/5 text-left text-xs text-marfim-400 uppercase tracking-wide">
                    <th className="px-5 py-3 font-medium">Investidor</th>
                    <th className="px-5 py-3 font-medium">Ativo</th>
                    <th className="px-5 py-3 font-medium text-right">Nominal</th>
                    <th className="px-5 py-3 font-medium text-right">Real</th>
                    <th className="px-5 py-3 font-medium text-right">Data</th>
                  </tr>
                </thead>
                <tbody>
                  {dados.simulacoes_recentes.map((s) => (
                    <tr key={s.id} className="border-b border-white/5 last:border-0">
                      <td className="px-5 py-3 text-marfim-200">{s.carteira__usuario__email}</td>
                      <td className="px-5 py-3 font-medium text-marfim-50">{s.ativo__ticker}</td>
                      <td className={`px-5 py-3 text-right numero font-medium ${Number(s.rentabilidade_nominal_pct) >= 0 ? "text-sucesso" : "text-perigo"}`}>
                        {formatarPct(s.rentabilidade_nominal_pct)}
                      </td>
                      <td className={`px-5 py-3 text-right numero font-medium ${Number(s.rentabilidade_real_pct) >= 0 ? "text-sucesso" : "text-perigo"}`}>
                        {formatarPct(s.rentabilidade_real_pct)}
                      </td>
                      <td className="px-5 py-3 text-right text-xs text-marfim-400">{formatarDataHora(s.criada_em)}</td>
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
