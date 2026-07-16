export default function CardIndicador({ rotulo, valor, variacao, destaque = false }) {
  const positivo = typeof variacao === "number" && variacao >= 0;
  return (
    <div className={`painel p-5 ${destaque ? "ring-1 ring-vivo-500/30" : ""}`}>
      <p className="text-xs font-medium text-marfim-400 uppercase tracking-wide">{rotulo}</p>
      <p className="numero text-2xl font-semibold text-marfim-50 mt-2">{valor}</p>
      {typeof variacao === "number" && (
        <p className={`numero text-sm mt-1.5 font-medium ${positivo ? "text-sucesso" : "text-perigo"}`}>
          {positivo ? "↑" : "↓"} {Math.abs(variacao).toFixed(2)}%
        </p>
      )}
    </div>
  );
}
