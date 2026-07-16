import { useState } from "react";
import { authApi } from "../services/api";
import { useAuth } from "../store/AuthContext";
import CabecalhoPagina from "../components/shared/CabecalhoPagina";

export default function PerfilPage() {
  const { user, atualizarUser } = useAuth();
  const [form, setForm] = useState({
    first_name: user?.first_name || "",
    last_name: user?.last_name || "",
    email: user?.email || "",
    phone: user?.phone || "",
    password_atual: "",
    nova_password: "",
  });
  const [mensagem, setMensagem] = useState(null);
  const [erro, setErro] = useState("");
  const [aGuardar, setAGuardar] = useState(false);

  const atualizar = (campo) => (e) => setForm((f) => ({ ...f, [campo]: e.target.value }));

  const submeter = async (e) => {
    e.preventDefault();
    setErro("");
    setMensagem(null);
    setAGuardar(true);
    try {
      const dados = { ...form };
      if (!dados.nova_password) {
        delete dados.nova_password;
        delete dados.password_atual;
      }
      const atualizado = await authApi.editarPerfil(dados);
      atualizarUser(atualizado);
      setMensagem("Perfil atualizado com sucesso.");
      setForm((f) => ({ ...f, password_atual: "", nova_password: "" }));
    } catch (e) {
      setErro(e.message || "Não foi possível guardar as alterações.");
    } finally {
      setAGuardar(false);
    }
  };

  return (
    <div>
      <CabecalhoPagina titulo="O meu perfil" subtitulo="Consulte e edite os seus dados pessoais." />

      <div className="p-8 max-w-lg">
        <form onSubmit={submeter} className="painel p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="rotulo">Nome</label>
              <input className="campo" value={form.first_name} onChange={atualizar("first_name")} />
            </div>
            <div>
              <label className="rotulo">Apelido</label>
              <input className="campo" value={form.last_name} onChange={atualizar("last_name")} />
            </div>
          </div>
          <div>
            <label className="rotulo">Email</label>
            <input type="email" className="campo" value={form.email} onChange={atualizar("email")} />
          </div>
          <div>
            <label className="rotulo">Telefone</label>
            <input className="campo" value={form.phone} onChange={atualizar("phone")} />
          </div>

          <div className="border-t border-white/5 pt-4">
            <p className="text-xs font-medium text-marfim-300 mb-3">Alterar palavra-passe (opcional)</p>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="rotulo">Palavra-passe atual</label>
                <input type="password" className="campo" value={form.password_atual} onChange={atualizar("password_atual")} />
              </div>
              <div>
                <label className="rotulo">Nova palavra-passe</label>
                <input type="password" className="campo" value={form.nova_password} onChange={atualizar("nova_password")} />
              </div>
            </div>
          </div>

          {mensagem && <div className="text-sm bg-sucesso-bg text-sucesso rounded-xl px-3.5 py-2.5">{mensagem}</div>}
          {erro && <div className="text-sm bg-perigo-bg text-perigo rounded-xl px-3.5 py-2.5">{erro}</div>}

          <button type="submit" className="btn-primario" disabled={aGuardar}>
            {aGuardar ? "A guardar..." : "Guardar alterações"}
          </button>
        </form>
      </div>
    </div>
  );
}
