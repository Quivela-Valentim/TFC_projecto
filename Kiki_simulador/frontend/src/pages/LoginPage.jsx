import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../store/AuthContext";
import { ApiError } from "../services/api";
import AuthLayout from "./AuthLayout";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [erro, setErro] = useState("");
  const [bloqueado, setBloqueado] = useState(false);
  const [aEnviar, setAEnviar] = useState(false);

  const submeter = async (e) => {
    e.preventDefault();
    setErro("");
    setBloqueado(false);

    if (!email || !password) {
      setErro("Todos os campos são obrigatórios, por favor preencha o email e a palavra-passe.");
      return;
    }

    setAEnviar(true);
    try {
      await login(email, password);
      navigate("/");
    } catch (e) {
      if (e instanceof ApiError && e.status === 423) {
        setBloqueado(true);
      }
      setErro(e.message || "Não foi possível entrar.");
    } finally {
      setAEnviar(false);
    }
  };

  return (
    <AuthLayout titulo="Entrar" subtitulo="Aceda à sua carteira fictícia de investimento.">
      <form onSubmit={submeter} className="space-y-4">
        <div>
          <label className="rotulo">Email</label>
          <input type="email" className="campo" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="voce@exemplo.ao" autoComplete="username" />
        </div>
        <div>
          <div className="flex items-center justify-between">
            <label className="rotulo">Palavra-passe</label>
            <Link to="/recuperar-password" className="text-xs text-vivo-400 hover:text-vivo-300 mb-1.5">
              Esqueceu-se da palavra-passe?
            </Link>
          </div>
          <input type="password" className="campo" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" autoComplete="current-password" />
        </div>

        {erro && (
          <div className={`text-sm rounded-[6px] px-3.5 py-2.5 ${bloqueado ? "bg-aviso-bg text-aviso" : "bg-perigo-bg text-perigo"}`}>
            {erro}
          </div>
        )}

        <button type="submit" className="btn-primario w-full" disabled={aEnviar}>
          {aEnviar ? "A entrar..." : "Entrar"}
        </button>
      </form>

      <p className="text-center text-sm text-marfim-300 mt-6">
        Ainda não tem conta?{" "}
        <Link to="/registo" className="text-vivo-400 hover:text-vivo-300 font-medium">
          Registe-se
        </Link>
      </p>
    </AuthLayout>
  );
}
