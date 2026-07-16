import { useEffect, useState } from "react";
import { adminApi } from "../../services/api";
import CabecalhoPagina from "../../components/shared/CabecalhoPagina";
import CardIndicador from "../../components/dashboard/CardIndicador";
import { formatarDataHora } from "../../utils/formatadores";

export default function MonitorPage() {
  const [dados, setDados] = useState(null);

  useEffect(() => {
    const carregar = () => adminApi.monitor().then(setDados);
    carregar();
    const intervalo = setInterval(carregar, 30000);
    return () => clearInterval(intervalo);
  }, []);

  if (!dados) return <div className="h-64 flex items-center justify-center"><div className="w-6 h-6 border-2 border-vivo-500 border-t-transparent rounded-full animate-spin" /></div>;

  return (
    <div>
      <CabecalhoPagina titulo="Monitorização do Sistema" subtitulo="Indicadores de funcionamento, atualizados automaticamente." />

      <div className="p-8 space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="painel p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-marfim-400 uppercase tracking-wide">Estado do sistema</p>
              <p className="font-display font-semibold text-marfim-50 mt-1 capitalize">{dados.estado_sistema}</p>
            </div>
            <span className="w-2.5 h-2.5 rounded-full bg-sucesso" />
          </div>
          <div className="painel p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-marfim-400 uppercase tracking-wide">Base de dados</p>
              <p className="font-display font-semibold text-marfim-50 mt-1 capitalize">{dados.estado_base_dados}</p>
            </div>
            <span className={`w-2.5 h-2.5 rounded-full ${dados.estado_base_dados === "ativo" ? "bg-sucesso" : "bg-perigo"}`} />
          </div>
          <CardIndicador rotulo="Última atualização de dados" valor={dados.ultima_atualizacao_dados ? formatarDataHora(dados.ultima_atualizacao_dados) : "—"} />
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <CardIndicador rotulo="Total de utilizadores" valor={dados.total_utilizadores} />
          <CardIndicador rotulo="Utilizadores ativos" valor={dados.utilizadores_ativos} />
          <CardIndicador rotulo="Utilizadores bloqueados" valor={dados.utilizadores_bloqueados} />
          <CardIndicador rotulo="Total de carteiras" valor={dados.total_carteiras} />
          <CardIndicador rotulo="Total de simulações" valor={dados.total_simulacoes} />
          <CardIndicador rotulo="Taxas de inflação registadas" valor={dados.quantidade_taxas_inflacao} />
          <CardIndicador rotulo="Ativos com dados em falta" valor={dados.ativos_com_dados_em_falta} destaque={dados.ativos_com_dados_em_falta > 0} />
        </div>

        {dados.ativos_com_dados_em_falta > 0 && (
          <div className="text-sm bg-aviso-bg text-aviso rounded-xl px-4 py-3">
            Existem ativos sem preços históricos recentes (últimos 45 dias). Isto pode impedir simulações em
            períodos próximos da data atual — considere atualizar os dados em "Dados Financeiros".
          </div>
        )}
      </div>
    </div>
  );
}
