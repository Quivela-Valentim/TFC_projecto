import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../store/AuthContext";
import AuthLayout from "./AuthLayout";

const ESTADO_INICIAL = {
  first_name: "", last_name: "", email: "", username: "", phone: "", password: "", password2: "",
};

export default function RegistoPage() {
  const { registar } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(ESTADO_INICIAL);
  const [erro, setErro] = useState("");
  const [aEnviar, setAEnviar] = useState(false);

  const atualizar = (campo) => (e) => setForm((f) => ({ ...f, [campo]: e.target.value }));

  const submeter = async (e) => {
    e.preventDefault();
    setErro("");

    if (form.password !== form.password2) {
      setErro("As palavras-passe não coincidem.");
      return;
    }

    setAEnviar(true);
    try {
      await registar(form);
      navigate("/onboarding");
    } catch (e) {
      setErro(e.message || "Não foi possível concluir o registo.");
    } finally {
      setAEnviar(false);
    }
  };

  return (
    <AuthLayout titulo="Criar conta" subtitulo="Comece a simular investimentos na BODIVA sem risco real." largura="max-w-lg">
      <form onSubmit={submeter} className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="rotulo">Nome</label>
            <input className="campo" value={form.first_name} onChange={atualizar("first_name")} required />
          </div>
          <div>
            <label className="rotulo">Apelido</label>
            <input className="campo" value={form.last_name} onChange={atualizar("last_name")} required />
          </div>
        </div>
        <div>
          <label className="rotulo">Nome de utilizador</label>
          <input className="campo" value={form.username} onChange={atualizar("username")} required />
          <p className="text-xs text-marfim-400 mt-1">Sem espaços — usa letras, números, ou . _ + -</p>
        </div>
        <div>
          <label className="rotulo">Email</label>
          <input type="email" className="campo" value={form.email} onChange={atualizar("email")} required />
        </div>
        <div>
          <label className="rotulo">Telefone (opcional)</label>
          <input className="campo" value={form.phone} onChange={atualizar("phone")} />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="rotulo">Palavra-passe</label>
            <input type="password" className="campo" value={form.password} onChange={atualizar("password")} required />
          </div>
          <div>
            <label className="rotulo">Confirmar palavra-passe</label>
            <input type="password" className="campo" value={form.password2} onChange={atualizar("password2")} required />
          </div>
        </div>
        <p className="text-xs text-marfim-400">Mínimo 8 caracteres, com letras e números. Não pode ser igual ao email ou ao nome.</p>

        {erro && <div className="text-sm mensagem rounded-[6px] px-3.5 py-2.5">{erro}</div>}

        <button type="submit" className="btn-primario w-full" disabled={aEnviar}>
          {aEnviar ? "A criar conta..." : "Criar conta"}
        </button>
      </form>

      <p className="text-center text-sm text-marfim-300 mt-6">
        Já tem conta?{" "}
        <Link to="/login" className="text-vivo-400 hover:text-vivo-300 font-medium">
          Entrar
        </Link>
      </p>
    </AuthLayout>
  );
}
