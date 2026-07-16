import { useEffect, useState } from "react";
import { adminApi } from "../../services/api";
import CabecalhoPagina from "../../components/shared/CabecalhoPagina";
import { formatarAOA, formatarData } from "../../utils/formatadores";

const TIPOS = [
  { valor: "ACAO", rotulo: "Ação" },
  { valor: "OT", rotulo: "Obrigação do Tesouro" },
  { valor: "BT", rotulo: "Bilhete do Tesouro" },
];

const ATIVO_VAZIO = { ticker: "", nome: "", tipo: "ACAO", setor: "", preco_ultimo: "" };

export default function AtivosPage() {
  const [ativos, setAtivos] = useState([]);
  const [selecionado, setSelecionado] = useState(null);
  const [precos, setPrecos] = useState([]);
  const [novoAtivo, setNovoAtivo] = useState(ATIVO_VAZIO);
  const [mostrarForm, setMostrarForm] = useState(false);
  const [novoPreco, setNovoPreco] = useState({ data: "", preco_fecho: "", fonte: "BODIVA" });
  const [erro, setErro] = useState("");

  const carregarAtivos = () => adminApi.listarAtivos().then((r) => setAtivos(r.results || r));

  useEffect(() => {
    carregarAtivos();
  }, []);

  useEffect(() => {
    if (selecionado) {
      adminApi.precosHistoricos(selecionado.id).then((r) => setPrecos((r.results || r).slice().reverse()));
    }
  }, [selecionado]);

  const criarAtivo = async (e) => {
    e.preventDefault();
    setErro("");
    try {
      await adminApi.criarAtivo(novoAtivo);
      setNovoAtivo(ATIVO_VAZIO);
      setMostrarForm(false);
      carregarAtivos();
    } catch (e) {
      setErro(e.message);
    }
  };

  const inserirPreco = async (e) => {
    e.preventDefault();
    if (!selecionado) return;
    setErro("");
    try {
      await adminApi.inserirPrecoHistorico(selecionado.id, novoPreco);
      setNovoPreco({ data: "", preco_fecho: "", fonte: "BODIVA" });
      adminApi.precosHistoricos(selecionado.id).then((r) => setPrecos((r.results || r).slice().reverse()));
      carregarAtivos();
    } catch (e) {
      setErro(e.message);
    }
  };

  return (
    <div>
      <CabecalhoPagina
        titulo="Dados Financeiros"
        subtitulo="Gerir os ativos da BODIVA e o respetivo histórico de preços, recolhidos por raspagem manual (RF008)."
        acoes={<button className="btn-primario text-sm" onClick={() => setMostrarForm((v) => !v)}>+ Novo ativo</button>}
      />

      <div className="p-8 space-y-6">
        {erro && <div className="text-sm bg-perigo-bg text-perigo rounded-xl px-4 py-3">{erro}</div>}

        {mostrarForm && (
          <form onSubmit={criarAtivo} className="painel p-5 grid grid-cols-2 sm:grid-cols-5 gap-3 items-end">
            <div>
              <label className="rotulo">Ticker</label>
              <input className="campo" value={novoAtivo.ticker} onChange={(e) => setNovoAtivo({ ...novoAtivo, ticker: e.target.value })} required />
            </div>
            <div className="sm:col-span-2">
              <label className="rotulo">Nome</label>
              <input className="campo" value={novoAtivo.nome} onChange={(e) => setNovoAtivo({ ...novoAtivo, nome: e.target.value })} required />
            </div>
            <div>
              <label className="rotulo">Tipo</label>
              <select className="campo" value={novoAtivo.tipo} onChange={(e) => setNovoAtivo({ ...novoAtivo, tipo: e.target.value })}>
                {TIPOS.map((t) => <option key={t.valor} value={t.valor}>{t.rotulo}</option>)}
              </select>
            </div>
            <div>
              <label className="rotulo">Preço inicial (Kz)</label>
              <input type="number" step="0.0001" className="campo" value={novoAtivo.preco_ultimo} onChange={(e) => setNovoAtivo({ ...novoAtivo, preco_ultimo: e.target.value })} required />
            </div>
            <button type="submit" className="btn-primario sm:col-span-5">Criar ativo</button>
          </form>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="painel overflow-hidden lg:col-span-1">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/5 text-left text-xs text-marfim-400 uppercase tracking-wide">
                  <th className="px-4 py-3 font-medium">Ticker</th>
                  <th className="px-4 py-3 font-medium text-right">Preço</th>
                </tr>
              </thead>
              <tbody>
                {ativos.map((a) => (
                  <tr key={a.id} onClick={() => setSelecionado(a)} className={`border-b border-white/5 last:border-0 cursor-pointer ${selecionado?.id === a.id ? "bg-vivo-500/10" : "hover:bg-white/[0.02]"}`}>
                    <td className="px-4 py-3">
                      <p className="font-medium text-marfim-50">{a.ticker}</p>
                      <p className="text-xs text-marfim-400 truncate max-w-[140px]">{a.nome}</p>
                    </td>
                    <td className="px-4 py-3 text-right numero text-marfim-200">{formatarAOA(a.preco_ultimo)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="lg:col-span-2 space-y-4">
            {selecionado ? (
              <>
                <form onSubmit={inserirPreco} className="painel p-5 flex items-end gap-3 flex-wrap">
                  <div>
                    <label className="rotulo">Data</label>
                    <input type="date" className="campo" value={novoPreco.data} onChange={(e) => setNovoPreco({ ...novoPreco, data: e.target.value })} max={new Date().toISOString().slice(0, 10)} required />
                  </div>
                  <div>
                    <label className="rotulo">Preço de fecho (Kz)</label>
                    <input type="number" step="0.0001" className="campo" value={novoPreco.preco_fecho} onChange={(e) => setNovoPreco({ ...novoPreco, preco_fecho: e.target.value })} required />
                  </div>
                  <div>
                    <label className="rotulo">Fonte</label>
                    <input className="campo" value={novoPreco.fonte} onChange={(e) => setNovoPreco({ ...novoPreco, fonte: e.target.value })} />
                  </div>
                  <button type="submit" className="btn-primario">Inserir preço — {selecionado.ticker}</button>
                </form>

                <div className="painel overflow-hidden max-h-[420px] overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead className="sticky top-0 bg-base-800">
                      <tr className="border-b border-white/5 text-left text-xs text-marfim-400 uppercase tracking-wide">
                        <th className="px-4 py-3 font-medium">Data</th>
                        <th className="px-4 py-3 font-medium text-right">Preço de fecho</th>
                        <th className="px-4 py-3 font-medium text-right">Fonte</th>
                      </tr>
                    </thead>
                    <tbody>
                      {precos.map((p) => (
                        <tr key={p.id} className="border-b border-white/5 last:border-0">
                          <td className="px-4 py-2.5 text-marfim-200">{formatarData(p.data)}</td>
                          <td className="px-4 py-2.5 text-right numero text-marfim-200">{formatarAOA(p.preco_fecho)}</td>
                          <td className="px-4 py-2.5 text-right text-xs text-marfim-400">{p.fonte}</td>
                        </tr>
                      ))}
                      {precos.length === 0 && (
                        <tr><td colSpan={3} className="px-4 py-6 text-center text-marfim-400">Sem preços históricos registados.</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </>
            ) : (
              <div className="painel p-8 text-center text-sm text-marfim-300">Selecione um ativo para gerir o histórico de preços.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
