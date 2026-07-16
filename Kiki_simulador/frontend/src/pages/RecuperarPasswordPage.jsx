import { useState } from "react";
import { Link } from "react-router-dom";
import { authApi } from "../services/api";
import AuthLayout from "./AuthLayout";

export default function RecuperarPasswordPage() {
  const [email, setEmail] = useState("");
  const [enviado, setEnviado] = useState(false);
  const [erro, setErro] = useState("");
  const [aEnviar, setAEnviar] = useState(false);

  const submeter = async (e) => {
    e.preventDefault();
    setErro("");
    setAEnviar(true);
    try {
      await authApi.pedirRecuperacao(email);
      setEnviado(true);
    } catch (e) {
      setErro(e.message || "Não foi possível processar o pedido.");
    } finally {
      setAEnviar(false);
    }
  };

  return (
    <AuthLayout titulo="Recuperar palavra-passe" subtitulo="Introduza o email associado à sua conta.">
      {enviado ? (
        <div className="text-sm bg-sucesso-bg text-sucesso rounded-[6px] px-3.5 py-3">
          Se o email estiver registado, enviámos uma ligação de recuperação. Verifique a sua caixa de entrada.
        </div>
      ) : (
        <form onSubmit={submeter} className="space-y-4">
          <div>
            <label className="rotulo">Email</label>
            <input type="email" className="campo" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          {erro && <div className="text-sm bg-perigo-bg text-perigo rounded-[6px] px-3.5 py-2.5">{erro}</div>}
          <button type="submit" className="btn-primario w-full" disabled={aEnviar}>
            {aEnviar ? "A enviar..." : "Enviar ligação de recuperação"}
          </button>
        </form>
      )}
      <p className="text-center text-sm text-marfim-300 mt-6">
        <Link to="/login" className="text-vivo-400 hover:text-vivo-300 font-medium">
          Voltar ao login
        </Link>
      </p>
    </AuthLayout>
  );
}
