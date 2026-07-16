import { useCallback, useEffect, useState } from "react";
import { carteiraApi } from "../services/api";
import CabecalhoPagina from "../components/shared/CabecalhoPagina";
import TabelaPosicoes from "../components/dashboard/TabelaPosicoes";
import ModalAdicionarAtivo from "../components/dashboard/ModalAdicionarAtivo";
import { formatarAOA } from "../utils/formatadores";

export default function CarteiraPage() {
  const [carteira, setCarteira] = useState(null);
  const [posicoes, setPosicoes] = useState(null);
  const [modalAberto, setModalAberto] = useState(false);
  const [erro, setErro] = useState("");

  const carregar = useCallback(() => {
    Promise.all([carteiraApi.obter(), carteiraApi.posicoes()])
      .then(([c, p]) => {
        setCarteira(c);
        setPosicoes(p.results || p);
      })
      .catch((e) => setErro(e.message));
  }, []);

  useEffect(() => {
    carregar();
  }, [carregar]);

  const remover = async (posicaoId) => {
    await carteiraApi.removerAtivo(posicaoId);
    carregar();
  };

  return (
    <div>
      <CabecalhoPagina
        titulo={carteira?.nome || "A minha carteira"}
        subtitulo={carteira?.descricao || "Composição da carteira fictícia."}
        acoes={
          <button className="btn-primario text-sm" onClick={() => setModalAberto(true)}>
            + Adicionar ativo
          </button>
        }
      />

      <div className="p-4 sm:p-8 space-y-6">
        {erro && <div className="text-sm bg-perigo-bg text-perigo rounded-[6px] px-4 py-3">{erro}</div>}

        {carteira && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="painel p-5">
              <p className="text-xs font-medium text-marfim-400 uppercase tracking-wide">Valor investido</p>
              <p className="numero text-2xl font-semibold text-marfim-50 mt-2">{formatarAOA(carteira.valor_investido)}</p>
            </div>
            <div className="painel p-5">
              <p className="text-xs font-medium text-marfim-400 uppercase tracking-wide">Valor atual</p>
              <p className="numero text-2xl font-semibold text-marfim-50 mt-2">{formatarAOA(carteira.valor_atual)}</p>
            </div>
          </div>
        )}

        {posicoes && <TabelaPosicoes posicoes={posicoes} onRemover={remover} />}
      </div>

      <ModalAdicionarAtivo aberto={modalAberto} onFechar={() => setModalAberto(false)} onAdicionado={carregar} />
    </div>
  );
}
