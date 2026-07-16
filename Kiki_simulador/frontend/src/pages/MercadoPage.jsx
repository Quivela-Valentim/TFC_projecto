import { useEffect, useState } from "react";
import { mercadoApi } from "../services/api";
import CabecalhoPagina from "../components/shared/CabecalhoPagina";
import GraficoEvolucao from "../components/dashboard/GraficoEvolucao";
import { formatarAOA, formatarPct } from "../utils/formatadores";

const TIPOS = [
  { valor: "", rotulo: "Todos" },
  { valor: "ACAO", rotulo: "Ações" },
  { valor: "OT", rotulo: "Obrigações do Tesouro" },
  { valor: "BT", rotulo: "Bilhetes do Tesouro" },
];

export default function MercadoPage() {
  const [ativos, setAtivos] = useState([]);
  const [tipo, setTipo] = useState("");
  const [selecionado, setSelecionado] = useState(null);
  const [historico, setHistorico] = useState([]);
  const [inflacao, setInflacao] = useState([]);

  useEffect(() => {
    mercadoApi.listar(tipo).then((r) => {
      const lista = r.results || r;
      setAtivos(lista);
      if (lista.length > 0) setSelecionado(lista[0]);
    });
  }, [tipo]);

  useEffect(() => {
    if (selecionado) {
      mercadoApi.historico(selecionado.id).then((r) => setHistorico(r.results || r));
    }
  }, [selecionado]);

  useEffect(() => {
    mercadoApi.inflacao().then((r) => setInflacao((r.results || r).slice(0, 12)));
  }, []);

  return (
    <div>
      <CabecalhoPagina titulo="Mercado BODIVA" subtitulo="Catálogo de ativos disponíveis e respetivo histórico de preços." />

      <div className="p-8 space-y-6">
        <div className="flex gap-2">
          {TIPOS.map((t) => (
            <button
              key={t.valor}
              onClick={() => setTipo(t.valor)}
              className={`text-xs font-medium px-3.5 py-2 rounded-xl transition ${
                tipo === t.valor ? "bg-vivo-500 text-white" : "bg-base-800 text-marfim-300 hover:bg-base-700"
              }`}
            >
              {t.rotulo}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="painel overflow-hidden lg:col-span-1">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/5 text-left text-xs text-marfim-400 uppercase tracking-wide">
                  <th className="px-4 py-3 font-medium">Ticker</th>
                  <th className="px-4 py-3 font-medium text-right">Preço</th>
                  <th className="px-4 py-3 font-medium text-right">Var.</th>
                </tr>
              </thead>
              <tbody>
                {ativos.map((a) => (
                  <tr
                    key={a.id}
                    onClick={() => setSelecionado(a)}
                    className={`border-b border-white/5 last:border-0 cursor-pointer transition ${
                      selecionado?.id === a.id ? "bg-vivo-500/10" : "hover:bg-white/[0.02]"
                    }`}
                  >
                    <td className="px-4 py-3">
                      <p className="font-medium text-marfim-50">{a.ticker}</p>
                      <p className="text-xs text-marfim-400 truncate max-w-[140px]">{a.nome}</p>
                    </td>
                    <td className="px-4 py-3 text-right numero text-marfim-200">{formatarAOA(a.preco_ultimo)}</td>
                    <td className={`px-4 py-3 text-right numero text-xs font-medium ${Number(a.variacao_percentual) >= 0 ? "text-sucesso" : "text-perigo"}`}>
                      {a.variacao_percentual != null ? formatarPct(a.variacao_percentual) : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="lg:col-span-2 painel p-6">
            {selecionado ? (
              <>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="font-display font-semibold text-marfim-50">{selecionado.ticker}</h2>
                    <p className="text-xs text-marfim-400">{selecionado.nome}</p>
                  </div>
                  {selecionado.taxa_juro_nominal && (
                    <span className="text-xs text-marfim-300">Taxa nominal: {formatarPct(selecionado.taxa_juro_nominal)}</span>
                  )}
                </div>
                <GraficoEvolucao dados={historico} />
              </>
            ) : (
              <p className="text-sm text-marfim-300">Selecione um ativo para ver o histórico.</p>
            )}
          </div>
        </div>

        <div>
          <h2 className="font-display font-semibold text-marfim-50 mb-3">Inflação (IPC mensal — últimos 12 meses)</h2>
          <div className="painel overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/5 text-left text-xs text-marfim-400 uppercase tracking-wide">
                  <th className="px-4 py-3 font-medium">Período</th>
                  <th className="px-4 py-3 font-medium text-right">IPC mensal</th>
                  <th className="px-4 py-3 font-medium text-right">Fonte</th>
                </tr>
              </thead>
              <tbody>
                {inflacao.map((i) => (
                  <tr key={`${i.ano}-${i.mes}`} className="border-b border-white/5 last:border-0">
                    <td className="px-4 py-2.5 text-marfim-200">{String(i.mes).padStart(2, "0")}/{i.ano}</td>
                    <td className="px-4 py-2.5 text-right numero text-marfim-200">{formatarPct(i.ipc_mensal)}</td>
                    <td className="px-4 py-2.5 text-right text-xs text-marfim-400">{i.fonte}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
