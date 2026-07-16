import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { carteiraApi } from "../services/api";
import { useAuth } from "../store/AuthContext";
import AuthLayout from "./AuthLayout";

export default function OnboardingPage() {
  const { atualizarUser } = useAuth();
  const navigate = useNavigate();
  const [nome, setNome] = useState("");
  const [descricao, setDescricao] = useState("");
  const [erro, setErro] = useState("");
  const [aEnviar, setAEnviar] = useState(false);

  const submeter = async (e) => {
    e.preventDefault();
    setErro("");
    setAEnviar(true);
    try {
      await carteiraApi.criar({ nome, descricao });
      atualizarUser({ tem_carteira: true });
      navigate("/dashboard");
    } catch (e) {
      setErro(e.message || "Não foi possível criar a carteira.");
    } finally {
      setAEnviar(false);
    }
  };

  return (
    <AuthLayout
      titulo="Criar a sua carteira fictícia"
      subtitulo="Cada investidor tem direito a uma única carteira, usada para todas as simulações."
    >
      <form onSubmit={submeter} className="space-y-4">
        <div>
          <label className="rotulo">Nome da carteira</label>
          <input className="campo" value={nome} onChange={(e) => setNome(e.target.value)} placeholder="Ex: Carteira de Reforma" required minLength={3} />
        </div>
        <div>
          <label className="rotulo">Descrição (opcional)</label>
          <textarea className="campo resize-none" rows={3} value={descricao} onChange={(e) => setDescricao(e.target.value)} placeholder="Objetivo desta carteira..." />
        </div>

        {erro && <div className="text-sm bg-perigo-bg text-perigo rounded-xl px-3.5 py-2.5">{erro}</div>}

        <button type="submit" className="btn-primario w-full" disabled={aEnviar}>
          {aEnviar ? "A criar..." : "Criar carteira"}
        </button>
      </form>
    </AuthLayout>
  );
}
