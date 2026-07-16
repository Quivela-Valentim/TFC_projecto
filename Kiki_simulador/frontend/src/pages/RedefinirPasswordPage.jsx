import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { authApi } from "../services/api";
import AuthLayout from "./AuthLayout";

export default function RedefinirPasswordPage() {
  const { uid, token } = useParams();
  const navigate = useNavigate();
  const [novaPassword, setNovaPassword] = useState("");
  const [confirmar, setConfirmar] = useState("");
  const [erro, setErro] = useState("");
  const [sucesso, setSucesso] = useState(false);
  const [aEnviar, setAEnviar] = useState(false);

  const submeter = async (e) => {
    e.preventDefault();
    setErro("");
    if (novaPassword !== confirmar) {
      setErro("As palavras-passe não coincidem.");
      return;
    }
    setAEnviar(true);
    try {
      await authApi.confirmarRecuperacao(uid, token, novaPassword);
      setSucesso(true);
      setTimeout(() => navigate("/login"), 2000);
    } catch (e) {
      setErro(e.message || "Não foi possível redefinir a palavra-passe.");
    } finally {
      setAEnviar(false);
    }
  };

  if (sucesso) {
    return (
      <AuthLayout titulo="Palavra-passe redefinida">
        <div className="text-sm bg-sucesso-bg text-sucesso rounded-[6px] px-3.5 py-3">
          A sua palavra-passe foi actualizada. A redireccionar para o login...
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout titulo="Definir nova palavra-passe">
      <form onSubmit={submeter} className="space-y-4">
        <div>
          <label className="rotulo">Nova palavra-passe</label>
          <input type="password" className="campo" value={novaPassword} onChange={(e) => setNovaPassword(e.target.value)} required />
        </div>
        <div>
          <label className="rotulo">Confirmar nova palavra-passe</label>
          <input type="password" className="campo" value={confirmar} onChange={(e) => setConfirmar(e.target.value)} required />
        </div>
        <p className="text-xs text-marfim-400">Mínimo 8 caracteres, com letras e números.</p>
        {erro && <div className="text-sm bg-perigo-bg text-perigo rounded-[6px] px-3.5 py-2.5">{erro}</div>}
        <button type="submit" className="btn-primario w-full" disabled={aEnviar}>
          {aEnviar ? "A guardar..." : "Redefinir palavra-passe"}
        </button>
      </form>
      <p className="text-center text-sm text-marfim-300 mt-6">
        <Link to="/login" className="text-vivo-400 hover:text-vivo-300 font-medium">
          Voltar ao login
        </Link>
      </p>
    </AuthLayout>
  );
}
