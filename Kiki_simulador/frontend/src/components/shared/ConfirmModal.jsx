export default function ConfirmModal({ aberto, titulo, mensagem, corBotao = "primario", onConfirmar, onCancelar, aProcessar }) {
  if (!aberto) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
      <div className="painel w-full max-w-sm p-6">
        <h3 className="font-display font-semibold text-lg text-marfim-50">{titulo}</h3>
        <p className="mt-2 text-sm text-marfim-300 leading-relaxed">{mensagem}</p>
        <div className="mt-6 flex justify-end gap-3">
          <button className="btn-secundario" onClick={onCancelar} disabled={aProcessar}>
            Cancelar
          </button>
          <button
            className={corBotao === "perigo" ? "btn-perigo" : "btn-primario"}
            onClick={onConfirmar}
            disabled={aProcessar}
          >
            {aProcessar ? "A processar..." : "Sim, confirmar"}
          </button>
        </div>
      </div>
    </div>
  );
}
