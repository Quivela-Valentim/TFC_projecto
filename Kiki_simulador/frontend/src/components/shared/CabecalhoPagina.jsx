export default function CabecalhoPagina({ titulo, subtitulo, acoes }) {
  return (
    <div className="flex items-start justify-between gap-4 px-8 py-6 border-b border-white/5">
      <div>
        <h1 className="font-display font-semibold text-xl text-marfim-50">{titulo}</h1>
        {subtitulo && <p className="text-sm text-marfim-300 mt-1">{subtitulo}</p>}
      </div>
      {acoes && <div className="flex items-center gap-2 flex-shrink-0">{acoes}</div>}
    </div>
  );
}
