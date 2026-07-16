import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { carteiraApi } from "../../services/api";

export default function FormSimulacao({ onSimular, aProcessar }) {
  const [posicoes, setPosicoes] = useState([]);
  const [ativoId, setAtivoId] = useState("");
  const [valor, setValor] = useState("");
  const [dataInicio, setDataInicio] = useState("");
  const [dataFim, setDataFim] = useState("");
  const [erroLocal, setErroLocal] = useState("");

  useEffect(() => {
    carteiraApi.posicoes().then((r) => setPosicoes(r.results || r));
  }, []);

  const submeter = (e) => {
    e.preventDefault();
    setErroLocal("");
    if (Number(valor) <= 0) {
      setErroLocal("O valor a investir deve ser superior a zero.");
      return;
    }
    if (dataInicio >= dataFim) {
      setErroLocal("A data de início deve ser anterior à data de fim.");
      return;
    }
    onSimular({ ativo_id: Number(ativoId), valor_investido: valor, data_inicio: dataInicio, data_fim: dataFim });
  };

  const hoje = new Date().toISOString().slice(0, 10);

  if (posicoes.length === 0) {
    return (
      <div className="painel p-6 space-y-3">
        <h2 className="font-display font-semibold text-marfim-50">Simular investimento</h2>
        <p className="text-sm text-marfim-300">
          Só é possível simular com ativos que já estejam na sua carteira. Adicione um ativo primeiro.
        </p>
        <Link to="/carteira" className="btn-primario inline-block text-sm">Ir para a Carteira</Link>
      </div>
    );
  }

  return (
    <form onSubmit={submeter} className="painel p-6 space-y-4">
      <h2 className="font-display font-semibold text-marfim-50">Simular investimento</h2>
      <p className="text-xs text-marfim-400 -mt-2">Apenas ativos já presentes na sua carteira podem ser simulados.</p>

      <div>
        <label className="rotulo">Ativo (da sua carteira)</label>
        <select className="campo" value={ativoId} onChange={(e) => setAtivoId(e.target.value)} required>
          <option value="">Selecione um ativo...</option>
          {posicoes.map((p) => (
            <option key={p.ativo.id} value={p.ativo.id}>
              {p.ativo.ticker} — {p.ativo.nome} ({p.ativo.tipo === "ACAO" ? "Ação" : p.ativo.tipo === "OT" ? "Obrigação do Tesouro" : "Bilhete do Tesouro"})
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="rotulo">Montante a investir (Kz)</label>
        <input type="number" step="0.01" min="0.01" className="campo" value={valor} onChange={(e) => setValor(e.target.value)} required />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="rotulo">Data de início</label>
          <input type="date" className="campo" value={dataInicio} onChange={(e) => setDataInicio(e.target.value)} max={hoje} required />
        </div>
        <div>
          <label className="rotulo">Data de fim</label>
          <input type="date" className="campo" value={dataFim} onChange={(e) => setDataFim(e.target.value)} max={hoje} required />
        </div>
      </div>

      {erroLocal && <div className="text-sm bg-perigo-bg text-perigo rounded-[6px] px-3.5 py-2.5">{erroLocal}</div>}

      <button type="submit" className="btn-primario w-full" disabled={aProcessar}>
        {aProcessar ? "A calcular..." : "Simular"}
      </button>
    </form>
  );
}
