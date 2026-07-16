import { useState } from "react";
import { formatarAOA, formatarPct, formatarData } from "../../utils/formatadores";
import ConfirmModal from "../shared/ConfirmModal";

export default function TabelaPosicoes({ posicoes, onRemover }) {
  const [aRemover, setARemover] = useState(null);
  const [aProcessar, setAProcessar] = useState(false);

  const confirmarRemocao = async () => {
    setAProcessar(true);
    try {
      await onRemover(aRemover.id);
      setARemover(null);
    } finally {
      setAProcessar(false);
    }
  };

  if (!posicoes || posicoes.length === 0) {
    return (
      <div className="painel p-8 text-center">
        <p className="text-sm text-marfim-300">A sua carteira ainda não tem ativos.</p>
        <p className="text-xs text-marfim-400 mt-1">Adicione um ativo do mercado BODIVA para começar a simular.</p>
      </div>
    );
  }

  return (
    <>
      <div className="painel overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/5 text-left text-xs text-marfim-400 uppercase tracking-wide">
              <th className="px-5 py-3 font-medium">Ativo</th>
              <th className="px-5 py-3 font-medium text-right">Quantidade</th>
              <th className="px-5 py-3 font-medium text-right">Preço médio</th>
              <th className="px-5 py-3 font-medium text-right">Custo total</th>
              <th className="px-5 py-3 font-medium text-right">Valor atual</th>
              <th className="px-5 py-3 font-medium text-right">Rentabilidade</th>
              <th className="px-5 py-3 font-medium text-right">Compra simulada</th>
              <th className="px-5 py-3" />
            </tr>
          </thead>
          <tbody>
            {posicoes.map((p) => (
              <tr key={p.id} className="border-b border-white/5 last:border-0 hover:bg-white/[0.02]">
                <td className="px-5 py-3.5">
                  <p className="font-medium text-marfim-50">{p.ativo.ticker}</p>
                  <p className="text-xs text-marfim-400">{p.ativo.nome}</p>
                </td>
                <td className="px-5 py-3.5 text-right numero text-marfim-200">{Number(p.quantidade).toLocaleString("pt-PT")}</td>
                <td className="px-5 py-3.5 text-right numero text-marfim-200">{formatarAOA(p.preco_medio)}</td>
                <td className="px-5 py-3.5 text-right numero text-marfim-200">{formatarAOA(p.custo_total)}</td>
                <td className="px-5 py-3.5 text-right numero text-marfim-50 font-medium">{formatarAOA(p.valor_atual)}</td>
                <td className={`px-5 py-3.5 text-right numero font-medium ${Number(p.lucro_prejuizo_percentual) >= 0 ? "text-sucesso" : "text-perigo"}`}>
                  {formatarPct(p.lucro_prejuizo_percentual)}
                </td>
                <td className="px-5 py-3.5 text-right text-marfim-400 text-xs">{formatarData(p.data_simulada_compra)}</td>
                <td className="px-5 py-3.5 text-right">
                  <button onClick={() => setARemover(p)} className="text-xs text-perigo hover:underline">
                    Remover
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <ConfirmModal
        aberto={!!aRemover}
        titulo="Remover ativo da carteira"
        mensagem={aRemover ? `Tem a certeza que quer remover ${aRemover.ativo.ticker} da carteira? Esta ação não afeta o histórico de simulações já realizadas.` : ""}
        corBotao="perigo"
        aProcessar={aProcessar}
        onCancelar={() => setARemover(null)}
        onConfirmar={confirmarRemocao}
      />
    </>
  );
}
