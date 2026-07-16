// components/shared/Sidebar.jsx
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../store/AuthContext";

const Icon = ({ path, className = "w-[18px] h-[18px]" }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d={path} />
  </svg>
);

const ICONES = {
  dashboard: "M4 13h6V4H4v9Zm0 7h6v-5H4v5Zm10 0h6V11h-6v9Zm0-16v5h6V4h-6Z",
  carteira: "M3 7h18v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Zm0 0 2.2-3h13.6L21 7M16 13h.01",
  simulacao: "m3 17 5-5.5 4 4L21 6M21 6h-5M21 6v5",
  mercado: "M3 21h18M5 21V10l4-6h6l4 6v11M9 21v-6h6v6",
  utilizadores: "M17 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2M10 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm9 10v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75",
  inflacao: "M6 18 18 6M8 8.5A2.5 2.5 0 1 0 8 3.5a2.5 2.5 0 0 0 0 5Zm8 12a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5Z",
  logs: "M9 4h11v16H4V9m5-5L4 9m5-5v5H4",
  monitor: "M3 3v18h18M7 15l4-6 3 4 5-8",
  perfil: "M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z",
  sair: "M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9",
};

const NAV_INVESTIDOR = [
  { path: "/dashboard", label: "Dashboard", icone: "dashboard" },
  { path: "/carteira", label: "Carteira", icone: "carteira" },
  { path: "/simulacao", label: "Simulação", icone: "simulacao" },
  { path: "/mercado", label: "Mercado", icone: "mercado" },
];

const NAV_ADMIN = [
  { path: "/admin/dashboard", label: "Dashboard", icone: "dashboard" },
  { path: "/admin/utilizadores", label: "Utilizadores", icone: "utilizadores" },
  { path: "/admin/ativos", label: "Dados Financeiros", icone: "mercado" },
  { path: "/admin/inflacao", label: "Inflação", icone: "inflacao" },
  { path: "/admin/logs", label: "Logs", icone: "logs" },
  { path: "/admin/monitor", label: "Monitorização", icone: "monitor" },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const isAdmin = user?.is_administrador;
  const nav = isAdmin ? NAV_ADMIN : NAV_INVESTIDOR;

  const sair = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <aside className="w-60 flex-shrink-0 bg-base-850 border-r border-white/5 flex flex-col min-h-screen">
      <div className="px-5 py-5 border-b border-white/5">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-vivo-500 rounded-lg flex items-center justify-center text-white text-sm font-display font-bold">B</div>
          <div>
            <p className="font-display font-semibold text-marfim-50 text-sm leading-none">BODIVA Sim</p>
            <p className="text-[11px] text-marfim-400 mt-1">{isAdmin ? "Painel Administrador" : "Simulador de Investimento"}</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {nav.map(({ path, label, icone }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition ${
                isActive ? "bg-vivo-500/15 text-vivo-400 font-medium" : "text-marfim-300 hover:text-marfim-50 hover:bg-white/5"
              }`
            }
          >
            <Icon path={ICONES[icone]} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="px-3 py-4 border-t border-white/5">
        <NavLink
          to="/perfil"
          className={({ isActive }) =>
            `flex items-center gap-3 px-3 py-2 mb-1 rounded-xl transition ${isActive ? "bg-white/5" : "hover:bg-white/5"}`
          }
        >
          <div className="w-7 h-7 rounded-full bg-base-600 flex items-center justify-center text-xs font-semibold text-marfim-100 flex-shrink-0">
            {(user?.first_name || user?.username || "?").charAt(0).toUpperCase()}
          </div>
          <div className="min-w-0">
            <p className="text-xs font-medium text-marfim-50 truncate">{user?.first_name || user?.username}</p>
            <p className="text-[11px] text-marfim-400 truncate">{user?.email}</p>
          </div>
        </NavLink>
        <button
          onClick={sair}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-sm text-marfim-300 hover:text-marfim-50 hover:bg-white/5 transition"
        >
          <Icon path={ICONES.sair} /> Sair
        </button>
      </div>
    </aside>
  );
}
