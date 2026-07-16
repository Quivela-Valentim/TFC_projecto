import { useEffect, useState } from "react";
import { adminApi } from "../../services/api";
import CabecalhoPagina from "../../components/shared/CabecalhoPagina";
import ConfirmModal from "../../components/shared/ConfirmModal";
import { formatarPct } from "../../utils/formatadores";

const MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];
const FORM_VAZIO = { ano: new Date().getFullYear(), mes: new Date().getMonth() + 1, ipc_mensal: "", fonte: "INE Angola" };

export default function InflacaoPage() {
  const [registos, setRegistos] = useState([]);
  const [form, setForm] = useState(FORM_VAZIO);
  const [aEliminar, setAEliminar] = useState(null);
  const [erro, setErro] = useState("");

  const carregar = () => adminApi.listarInflacao().then((r) => setRegistos(r.results || r));

  useEffect(() => {
    carregar();
  }, []);

  const submeter = async (e) => {
    e.preventDefault();
    setErro("");
    try {
      await adminApi.criarInflacao(form);
      setForm(FORM_VAZIO);
      carregar();
    } catch (e) {
      setErro(e.message);
    }
  };

  const confirmarEliminacao = async () => {
    try {
      await adminApi.eliminarInflacao(aEliminar.id);
      setAEliminar(null);
      carregar();
    } catch (e) {
      setErro(e.message);
    }
  };

  return (
    <div>
      <CabecalhoPagina titulo="Taxa de Inflação" subtitulo="IPC mensal de Angola, usado no cálculo da rentabilidade real (RN008)." />

      <div className="p-4 sm:p-8 space-y-6">
        {erro && <div className="text-sm mensagem rounded-[6px] px-4 py-3">{erro}</div>}

        <form onSubmit={submeter} className="painel p-5 flex items-end gap-3 flex-wrap">
          <div>
            <label className="rotulo">Ano</label>
            <input type="number" className="campo w-24" value={form.ano} onChange={(e) => setForm({ ...form, ano: Number(e.target.value) })} required />
          </div>
          <div>
            <label className="rotulo">Mês</label>
            <select className="campo w-32" value={form.mes} onChange={(e) => setForm({ ...form, mes: Number(e.target.value) })}>
              {MESES.map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
            </select>
          </div>
          <div>
            <label className="rotulo">IPC mensal (%)</label>
            <input type="number" step="0.0001" className="campo w-32" value={form.ipc_mensal} onChange={(e) => setForm({ ...form, ipc_mensal: e.target.value })} required />
          </div>
          <div>
            <label className="rotulo">Fonte</label>
            <input className="campo w-40" value={form.fonte} onChange={(e) => setForm({ ...form, fonte: e.target.value })} />
          </div>
          <button type="submit" className="btn-primario">Inserir</button>
        </form>

        <div className="painel overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/5 text-left text-xs text-marfim-400 uppercase tracking-wide">
                <th className="px-5 py-3 font-medium">Período</th>
                <th className="px-5 py-3 font-medium text-right">IPC mensal</th>
                <th className="px-5 py-3 font-medium">Fonte</th>
                <th className="px-5 py-3 font-medium text-right">Ações</th>
              </tr>
            </thead>
            <tbody>
              {registos.map((r) => (
                <tr key={r.id} className="border-b border-white/5 last:border-0 hover:bg-white/[0.02]">
                  <td className="px-5 py-3 text-marfim-50 font-medium">{MESES[r.mes - 1]}/{r.ano}</td>
                  <td className="px-5 py-3 text-right numero text-marfim-200">{formatarPct(r.ipc_mensal)}</td>
                  <td className="px-5 py-3 text-marfim-300 text-xs">{r.fonte}</td>
                  <td className="px-5 py-3 text-right">
                    <button className="text-xs text-perigo hover:underline" onClick={() => setAEliminar(r)}>Eliminar</button>
                  </td>
                </tr>
              ))}
              {registos.length === 0 && (
                <tr><td colSpan={4} className="px-5 py-8 text-center text-marfim-400">Sem registos de inflação.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <ConfirmModal
        aberto={!!aEliminar}
        titulo="Eliminar registo de inflação"
        mensagem={aEliminar ? `Eliminar o registo de ${MESES[aEliminar.mes - 1]}/${aEliminar.ano}? Simulações que dependam deste período deixarão de poder ser recalculadas.` : ""}
        corBotao="perigo"
        onCancelar={() => setAEliminar(null)}
        onConfirmar={confirmarEliminacao}
      />
    </div>
  );
}
