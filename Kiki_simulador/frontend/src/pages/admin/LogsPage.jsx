import { useEffect, useState } from "react";
import { adminApi } from "../../services/api";
import CabecalhoPagina from "../../components/shared/CabecalhoPagina";
import { formatarDataHora } from "../../utils/formatadores";

const TIPOS = [
  "", "LOGIN", "LOGIN_FALHADO", "LOGOUT", "CRIAR_CARTEIRA", "ADICIONAR_ATIVO",
  "REMOVER_ATIVO", "SIMULACAO", "GERIR_UTILIZADOR", "GERIR_INFLACAO",
  "GERIR_ATIVO", "CONSULTA_LOGS", "CONSULTA_DADOS_FINANCEIROS",
];

export default function LogsPage() {
  const [logs, setLogs] = useState([]);
  const [filtros, setFiltros] = useState({ inicio: "", fim: "", tipo: "" });
  const [aExportar, setAExportar] = useState(false);
  const [erroExportar, setErroExportar] = useState("");

  const parametrosAtivos = () => {
    const params = {};
    if (filtros.inicio) params.inicio = filtros.inicio;
    if (filtros.fim) params.fim = filtros.fim;
    if (filtros.tipo) params.tipo = filtros.tipo;
    return params;
  };

  const carregar = () => {
    adminApi.logs(parametrosAtivos()).then((r) => setLogs(r.results || r));
  };

  const emitirRelatorio = async () => {
    setErroExportar("");
    setAExportar(true);
    try {
      await adminApi.relatorioLogs(parametrosAtivos());
    } catch (e) {
      setErroExportar(e.message || "Não foi possível gerar o relatório.");
    } finally {
      setAExportar(false);
    }
  };

  useEffect(() => {
    carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div>
      <CabecalhoPagina
        titulo="Logs de Auditoria"
        subtitulo="Sem filtro de datas, mostra por defeito os últimos 30 dias."
        acoes={
          <button className="btn-secundario text-sm" onClick={emitirRelatorio} disabled={aExportar}>
            {aExportar ? "A gerar..." : "Emitir relatório administrativo"}
          </button>
        }
      />

      <div className="p-4 sm:p-8 space-y-6">
        {erroExportar && <div className="text-sm mensagem rounded-[6px] px-4 py-3">{erroExportar}</div>}

        <div className="painel p-5 flex items-end gap-3 flex-wrap">
          <div>
            <label className="rotulo">De</label>
            <input type="date" className="campo" value={filtros.inicio} onChange={(e) => setFiltros({ ...filtros, inicio: e.target.value })} />
          </div>
          <div>
            <label className="rotulo">Até</label>
            <input type="date" className="campo" value={filtros.fim} onChange={(e) => setFiltros({ ...filtros, fim: e.target.value })} />
          </div>
          <div>
            <label className="rotulo">Tipo</label>
            <select className="campo w-52" value={filtros.tipo} onChange={(e) => setFiltros({ ...filtros, tipo: e.target.value })}>
              {TIPOS.map((t) => <option key={t} value={t}>{t || "Todos"}</option>)}
            </select>
          </div>
          <button className="btn-primario" onClick={carregar}>Filtrar</button>
        </div>

        <div className="painel overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/5 text-left text-xs text-marfim-400 uppercase tracking-wide">
                <th className="px-5 py-3 font-medium">Tipo</th>
                <th className="px-5 py-3 font-medium">Utilizador</th>
                <th className="px-5 py-3 font-medium">Detalhes</th>
                <th className="px-5 py-3 font-medium">IP</th>
                <th className="px-5 py-3 font-medium text-right">Data/Hora</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((l) => (
                <tr key={l.id} className="border-b border-white/5 last:border-0 hover:bg-white/[0.02]">
                  <td className="px-5 py-2.5"><span className="text-xs font-medium px-2 py-1 rounded-lg bg-base-700 text-marfim-200">{l.tipo}</span></td>
                  <td className="px-5 py-2.5 text-marfim-300">{l.utilizador_email || l.identificador_tentativa || "—"}</td>
                  <td className="px-5 py-2.5 text-xs text-marfim-400 max-w-xs truncate">{l.detalhes}</td>
                  <td className="px-5 py-2.5 text-xs text-marfim-400">{l.endereco_ip || "—"}</td>
                  <td className="px-5 py-2.5 text-right text-xs text-marfim-400">{formatarDataHora(l.criado_em)}</td>
                </tr>
              ))}
              {logs.length === 0 && (
                <tr><td colSpan={5} className="px-5 py-8 text-center text-marfim-400">Sem registos para o período selecionado.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
