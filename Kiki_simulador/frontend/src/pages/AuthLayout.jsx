import { Link } from "react-router-dom";

export default function AuthLayout({ titulo, subtitulo, children, largura = "max-w-md" }) {
  return (
    <div className="min-h-screen bg-base-900 flex items-center justify-center px-4 py-10 relative overflow-hidden">
      {/* Assinatura visual: linhas de "cotação" subtis no fundo */}
      <svg className="absolute inset-0 w-full h-full opacity-[0.07] pointer-events-none" preserveAspectRatio="none" viewBox="0 0 800 400">
        <polyline points="0,300 80,280 160,320 240,250 320,270 400,180 480,220 560,140 640,190 720,110 800,150" fill="none" stroke="#5C8CFF" strokeWidth="2" />
        <polyline points="0,200 80,230 160,190 240,240 320,210 400,260 480,230 560,270 640,240 720,290 800,260" fill="none" stroke="#93A5C9" strokeWidth="1.5" />
      </svg>

      <div className={`w-full ${largura} relative`}>
        <Link to="/" className="flex items-center gap-2.5 justify-center mb-8 hover:opacity-80 transition">
          <div className="w-9 h-9 bg-vivo-500 rounded-lg flex items-center justify-center text-white font-display font-bold">K</div>
          <span className="font-display font-semibold text-marfim-50 text-lg">Kiki Simulador</span>
        </Link>
        <div className="painel p-8">
          <h1 className="font-display font-bold text-[32px] text-marfim-50">{titulo}</h1>
          {subtitulo && <p className="text-sm text-marfim-300 mt-1.5">{subtitulo}</p>}
          <div className="mt-6">{children}</div>
        </div>

        <p className="text-center text-xs text-marfim-400 mt-6">
          Simulador educacional — os resultados não constituem recomendações de investimento.
        </p>
      </div>
    </div>
  );
}
