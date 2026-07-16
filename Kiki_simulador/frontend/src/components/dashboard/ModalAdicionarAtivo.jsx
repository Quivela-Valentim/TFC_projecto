import { useEffect, useState } from "react";
import { carteiraApi, mercadoApi } from "../../services/api";

export default function ModalAdicionarAtivo({ aberto, onFechar, onAdicionado }) {
  const [ativos, setAtivos] = useState([]);
  const [ativoId, setAtivoId] = useState("");
  const [quantidade, setQuantidade] = useState("");
  const [data, setData] = useState("");
  const [erro, setErro] = useState("");
  const [aEnviar, setAEnviar] = useState(false);

  useEffect(() => {
    if (aberto) {
      mercadoApi.listar().then((r) => setAtivos(r.results || r));
      setErro("");
      setQuantidade("");
      setData("");
    }
  }, [aberto]);

  if (!aberto) return null;

  const submeter = async (e) => {
    e.preventDefault();
    setErro("");
    setAEnviar(true);
    try {
      await carteiraApi.adicionarAtivo({
        ativo_id: Number(ativoId),
        quantidade,
        data_simulada_compra: data,
      });
      onAdicionado();
      onFechar();
    } catch (e) {
      setErro(e.message || "Não foi possível adicionar o ativo.");
    } finally {
      setAEnviar(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
      <div className="painel w-full max-w-md p-6">
        <h3 className="font-display font-semibold text-lg text-marfim-50">Adicionar ativo à carteira</h3>
        <p className="text-sm text-marfim-300 mt-1">
          A compra é registada ao preço histórico da data escolhida, nunca a um preço em tempo real.
        </p>

        <form onSubmit={submeter} className="space-y-4 mt-5">
          <div>
            <label className="rotulo">Ativo</label>
            <select className="campo" value={ativoId} onChange={(e) => setAtivoId(e.target.value)} required>
              <option value="">Selecione um ativo...</option>
              {ativos.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.ticker} — {a.nome}
                </option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="rotulo">Quantidade</label>
              <input type="number" step="0.0001" min="0.0001" className="campo" value={quantidade} onChange={(e) => setQuantidade(e.target.value)} required />
            </div>
            <div>
              <label className="rotulo">Data simulada da compra</label>
              <input type="date" className="campo" value={data} onChange={(e) => setData(e.target.value)} max={new Date().toISOString().slice(0, 10)} required />
            </div>
          </div>

          {erro && <div className="text-sm mensagem rounded-[6px] px-3.5 py-2.5">{erro}</div>}

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" className="btn-secundario" onClick={onFechar} disabled={aEnviar}>
              Cancelar
            </button>
            <button type="submit" className="btn-primario" disabled={aEnviar}>
              {aEnviar ? "A adicionar..." : "Adicionar"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
