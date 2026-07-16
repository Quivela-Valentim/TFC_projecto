import { useCallback, useEffect, useState } from "react";
import { adminApi } from "../../services/api";
import CabecalhoPagina from "../../components/shared/CabecalhoPagina";
import EstadoBadge from "../../components/shared/EstadoBadge";
import ConfirmModal from "../../components/shared/ConfirmModal";
import { formatarData } from "../../utils/formatadores";

export default function UtilizadoresPage() {
  const [utilizadores, setUtilizadores] = useState([]);
  const [pesquisa, setPesquisa] = useState("");
  const [acaoPendente, setAcaoPendente] = useState(null); // { tipo, utilizador }
  const [aProcessar, setAProcessar] = useState(false);
  const [erro, setErro] = useState("");

  const carregar = useCallback(() => {
    adminApi.utilizadores(pesquisa).then((r) => setUtilizadores(r.results || r)).catch((e) => setErro(e.message));
  }, [pesquisa]);

  useEffect(() => {
    const t = setTimeout(carregar, 300);
    return () => clearTimeout(t);
  }, [carregar]);

  const confirmar = async () => {
    if (!acaoPendente) return;
    setAProcessar(true);
    try {
      const { tipo, utilizador } = acaoPendente;
      if (tipo === "bloquear") await adminApi.bloquearUtilizador(utilizador.id);
      if (tipo === "desbloquear") await adminApi.desbloquearUtilizador(utilizador.id);
      if (tipo === "excluir") await adminApi.excluirUtilizador(utilizador.id);
      setAcaoPendente(null);
      carregar();
    } catch (e) {
      setErro(e.message);
    } finally {
      setAProcessar(false);
    }
  };

  const TEXTOS = {
    bloquear: (u) => `Tem a certeza que quer bloquear a conta de ${u.first_name || u.email}?`,
    desbloquear: (u) => `Tem a certeza que quer desbloquear a conta de ${u.first_name || u.email}?`,
    excluir: (u) => `Tem a certeza que quer excluir permanentemente a conta de ${u.first_name || u.email}? Esta ação não pode ser revertida.`,
  };

  return (
    <div>
      <CabecalhoPagina
        titulo="Gerir Utilizadores"
        subtitulo="Consultar, bloquear, desbloquear e excluir investidores registados."
        acoes={
          <input
            className="campo w-56"
            placeholder="Pesquisar por nome ou email..."
            value={pesquisa}
            onChange={(e) => setPesquisa(e.target.value)}
          />
        }
      />

     <div className="p-4 sm:p-8">
        {erro && <div className="text-sm bg-perigo-bg text-perigo rounded-[6px] px-4 py-3 mb-4">{erro}</div>}

        <div className="painel overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/5 text-left text-xs text-marfim-400 uppercase tracking-wide">
                <th className="px-5 py-3 font-medium">Investidor</th>
                <th className="px-5 py-3 font-medium">Email</th>
                <th className="px-5 py-3 font-medium">Estado</th>
                <th className="px-5 py-3 font-medium">Carteira</th>
                <th className="px-5 py-3 font-medium">Registado em</th>
                <th className="px-5 py-3 font-medium text-right">Ações</th>
              </tr>
            </thead>
            <tbody>
              {utilizadores.map((u) => (
                <tr key={u.id} className="border-b border-white/5 last:border-0 hover:bg-white/[0.02]">
                  <td className="px-5 py-3 font-medium text-marfim-50">{u.first_name} {u.last_name}</td>
                  <td className="px-5 py-3 text-marfim-300">{u.email}</td>
                  <td className="px-5 py-3"><EstadoBadge estado={u.estado} /></td>
                  <td className="px-5 py-3 text-marfim-300">{u.tem_carteira ? "Sim" : "Não"}</td>
                  <td className="px-5 py-3 text-xs text-marfim-400">{formatarData(u.created_at)}</td>
                  <td className="px-5 py-3 text-right space-x-3">
                    {u.estado === "ativo" ? (
                      <button className="text-xs text-aviso hover:underline" onClick={() => setAcaoPendente({ tipo: "bloquear", utilizador: u })}>
                        Bloquear
                      </button>
                    ) : (
                      <button className="text-xs text-sucesso hover:underline" onClick={() => setAcaoPendente({ tipo: "desbloquear", utilizador: u })}>
                        Desbloquear
                      </button>
                    )}
                    <button className="text-xs text-perigo hover:underline" onClick={() => setAcaoPendente({ tipo: "excluir", utilizador: u })}>
                      Excluir
                    </button>
                  </td>
                </tr>
              ))}
              {utilizadores.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-5 py-8 text-center text-marfim-400">Nenhum utilizador encontrado.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <ConfirmModal
        aberto={!!acaoPendente}
        titulo="Confirmar operação"
        mensagem={acaoPendente ? TEXTOS[acaoPendente.tipo](acaoPendente.utilizador) : ""}
        corBotao={acaoPendente?.tipo === "excluir" ? "perigo" : "primario"}
        aProcessar={aProcessar}
        onCancelar={() => setAcaoPendente(null)}
        onConfirmar={confirmar}
      />
    </div>
  );
}
