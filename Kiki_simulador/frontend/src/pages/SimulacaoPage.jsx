import { useCallback, useEffect, useState } from "react";
import { simulacaoApi } from "../services/api";
import CabecalhoPagina from "../components/shared/CabecalhoPagina";
import FormSimulacao from "../components/simulacao/FormSimulacao";
import ResultadoSimulacao from "../components/simulacao/ResultadoSimulacao";
import HistoricoSimulacoes from "../components/simulacao/HistoricoSimulacoes";
import ComparacaoSimulacoes from "../components/simulacao/ComparacaoSimulacoes";

export default function SimulacaoPage() {
  const [resultado, setResultado] = useState(null);
  const [historico, setHistorico] = useState([]);
  const [comparacao, setComparacao] = useState(null);
  const [erro, setErro] = useState("");
  const [aProcessar, setAProcessar] = useState(false);

  const carregarHistorico = useCallback(() => {
    simulacaoApi.historico().then((r) => setHistorico(r.results || r));
  }, []);

  useEffect(() => {
    carregarHistorico();
  }, [carregarHistorico]);

  const simular = async (dados) => {
    setErro("");
    setAProcessar(true);
    setResultado(null);
    try {
      const r = await simulacaoApi.simular(dados);
      setResultado(r);
      carregarHistorico();
    } catch (e) {
      setErro(e.message || "Não foi possível concluir a simulação.");
    } finally {
      setAProcessar(false);
    }
  };

  const comparar = async (ids) => {
    try {
      const r = await simulacaoApi.comparar(ids);
      setComparacao(r);
    } catch (e) {
      setErro(e.message);
    }
  };

  return (
    <div>
      <CabecalhoPagina titulo="Simulação de Investimento" subtitulo="Defina um montante e um período histórico para calcular a rentabilidade nominal e real." />

      <div className="p-4 sm:p-8 space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
          <FormSimulacao onSimular={simular} aProcessar={aProcessar} />
          <div>
            {erro && <div className="text-sm bg-perigo-bg text-perigo rounded-xl px-3.5 py-2.5 mb-4">{erro}</div>}
            {resultado ? (
              <ResultadoSimulacao resultado={resultado} />
            ) : (
              <div className="painel p-8 text-center text-sm text-marfim-300 h-full flex items-center justify-center">
                Preencha o formulário para ver o resultado da simulação aqui.
              </div>
            )}
          </div>
        </div>

        <HistoricoSimulacoes simulacoes={historico} onComparar={comparar} />
      </div>

      {comparacao && <ComparacaoSimulacoes simulacoes={comparacao} onFechar={() => setComparacao(null)} />}
    </div>
  );
}
