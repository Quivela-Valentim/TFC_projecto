export default function EstadoBadge({ estado }) {
  const ativo = estado === "ativo";
  return (
    <span className={ativo ? "badge-ativo" : "badge-bloqueado"}>
      <span className={`w-1.5 h-1.5 rounded-full ${ativo ? "bg-sucesso" : "bg-perigo"}`} />
      {ativo ? "Ativo" : "Bloqueado"}
    </span>
  );
}
