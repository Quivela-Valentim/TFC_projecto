import { Link } from "react-router-dom";

const CARACTERISTICAS = [
  {
    titulo: "Sem risco real",
    texto: "Investe de forma fictícia em Obrigações do Tesouro, Bilhetes do Tesouro e Ações da BODIVA, sem arriscar dinheiro a valer.",
    icone: "M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z",
  },
  {
    titulo: "Rentabilidade real, não só nominal",
    texto: "Cada simulação é ajustada à inflação de Angola, para veres o que o teu investimento realmente valeria — não só o que parece valer.",
    icone: "M2.25 18 9 11.25l4.306 4.306a11.95 11.95 0 0 1 5.814-5.518l2.74-1.22m0 0-5.94-2.281m5.94 2.28-2.28 5.941",
  },
  {
    titulo: "Histórico e comparação",
    texto: "Guarda todas as tuas simulações, compara cenários lado a lado, e exporta os resultados em PDF quando precisares.",
    icone: "M9 17.25v1.007a3 3 0 0 1-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0 1 15 18.257V17.25m6-12V15a2.25 2.25 0 0 1-2.25 2.25H5.25A2.25 2.25 0 0 1 3 15V5.25m18 0A2.25 2.25 0 0 0 18.75 3H5.25A2.25 2.25 0 0 0 3 5.25m18 0V12a2.25 2.25 0 0 1-2.25 2.25H5.25A2.25 2.25 0 0 1 3 12V5.25",
  },
];

export default function WelcomePage() {
  return (
    <div className="min-h-screen bg-base-900 relative overflow-hidden flex flex-col">
      {/* Assinatura visual: linhas de "cotação" subtis no fundo */}
      <svg className="absolute inset-0 w-full h-full opacity-[0.06] pointer-events-none" preserveAspectRatio="none" viewBox="0 0 800 400">
        <polyline points="0,300 80,280 160,320 240,250 320,270 400,180 480,220 560,140 640,190 720,110 800,150" fill="none" stroke="#5C8CFF" strokeWidth="2" />
        <polyline points="0,200 80,230 160,190 240,240 320,210 400,260 480,230 560,270 640,240 720,290 800,260" fill="none" stroke="#93A5C9" strokeWidth="1.5" />
      </svg>

      <header className="relative px-6 sm:px-10 py-6 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-vivo-500 rounded-lg flex items-center justify-center text-white font-display font-bold">K</div>
          <span className="font-display font-semibold text-marfim-50 text-lg">Kiki Simulador</span>
        </div>
        <Link to="/login" className="text-sm font-medium text-marfim-300 hover:text-marfim-50 transition">
          Entrar
        </Link>
      </header>

      <main className="relative flex-1 flex items-center px-6 sm:px-10">
        <div className="max-w-5xl mx-auto w-full py-12 sm:py-16">
          <div className="max-w-2xl">
            <span className="inline-block text-xs font-medium text-vivo-400 bg-vivo-500/10 px-3 py-1.5 rounded-full mb-6">
              Simulador educacional — sem dinheiro real envolvido
            </span>
            <h1 className="font-display font-bold text-[32px] sm:text-[44px] leading-[1.1] text-marfim-50">
              Simula os teus investimentos na BODIVA antes de arriscares a valer
            </h1>
            <p className="text-marfim-300 text-base sm:text-lg mt-5 leading-relaxed">
              Escolhe um ativo, um montante e um período histórico, e descobre não só o ganho aparente do teu
              investimento, mas a rentabilidade <span className="text-marfim-50 font-medium">real</span> — já
              ajustada à inflação de Angola.
            </p>

            <div className="flex flex-col sm:flex-row gap-3 mt-8">
              <Link to="/registo" className="btn-primario text-center">
                Criar conta gratuita
              </Link>
              <Link to="/login" className="btn-secundario text-center">
                Já tenho conta
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 mt-16">
            {CARACTERISTICAS.map((c) => (
              <div key={c.titulo} className="painel p-5">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" className="w-6 h-6 text-vivo-400 mb-3">
                  <path d={c.icone} />
                </svg>
                <h3 className="font-display font-semibold text-marfim-50 text-sm">{c.titulo}</h3>
                <p className="text-marfim-400 text-sm mt-1.5 leading-relaxed">{c.texto}</p>
              </div>
            ))}
          </div>
        </div>
      </main>

      <footer className="relative px-6 sm:px-10 py-6 text-center">
        <p className="text-xs text-marfim-400">
          Simulador educacional — os resultados não constituem recomendações de investimento.
        </p>
      </footer>
    </div>
  );
}