// src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./store/AuthContext";
import Sidebar from "./components/shared/Sidebar";

import LoginPage from "./pages/LoginPage";
import RegistoPage from "./pages/RegistoPage";
import RecuperarPasswordPage from "./pages/RecuperarPasswordPage";
import RedefinirPasswordPage from "./pages/RedefinirPasswordPage";
import OnboardingPage from "./pages/OnboardingPage";
import DashboardPage from "./pages/DashboardPage";
import CarteiraPage from "./pages/CarteiraPage";
import SimulacaoPage from "./pages/SimulacaoPage";
import MercadoPage from "./pages/MercadoPage";
import PerfilPage from "./pages/PerfilPage";

import AdminDashboardPage from "./pages/admin/AdminDashboardPage";
import UtilizadoresPage from "./pages/admin/UtilizadoresPage";
import AtivosPage from "./pages/admin/AtivosPage";
import InflacaoPage from "./pages/admin/InflacaoPage";
import LogsPage from "./pages/admin/LogsPage";
import MonitorPage from "./pages/admin/MonitorPage";

function Carregando() {
  return (
    <div className="min-h-screen bg-base-900 flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-vivo-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );
}

// Rota para investidor autenticado (bloqueia administradores)
function RotaInvestidor({ children }) {
  const { user, carregando } = useAuth();
  if (carregando) return <Carregando />;
  if (!user) return <Navigate to="/login" replace />;
  if (user.is_administrador) return <Navigate to="/admin/dashboard" replace />;
  if (!user.tem_carteira) return <Navigate to="/onboarding" replace />;
  return children;
}

// Rota para administrador autenticado (bloqueia investidores)
function RotaAdmin({ children }) {
  const { user, carregando } = useAuth();
  if (carregando) return <Carregando />;
  if (!user) return <Navigate to="/login" replace />;
  if (!user.is_administrador) return <Navigate to="/dashboard" replace />;
  return children;
}

function RotaOnboarding({ children }) {
  const { user, carregando } = useAuth();
  if (carregando) return <Carregando />;
  if (!user) return <Navigate to="/login" replace />;
  if (user.is_administrador) return <Navigate to="/admin/dashboard" replace />;
  if (user.tem_carteira) return <Navigate to="/dashboard" replace />;
  return children;
}

function RaizRedirect() {
  const { user, carregando } = useAuth();
  if (carregando) return <Carregando />;
  if (!user) return <Navigate to="/login" replace />;
  if (user.is_administrador) return <Navigate to="/admin/dashboard" replace />;
  if (!user.tem_carteira) return <Navigate to="/onboarding" replace />;
  return <Navigate to="/dashboard" replace />;
}

function ComSidebar({ children }) {
  return (
    <div className="flex min-h-screen bg-base-900">
      <Sidebar />
      <div className="flex-1 min-w-0">{children}</div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/registo" element={<RegistoPage />} />
          <Route path="/recuperar-password" element={<RecuperarPasswordPage />} />
          <Route path="/redefinir-password/:uid/:token" element={<RedefinirPasswordPage />} />
          <Route path="/onboarding" element={<RotaOnboarding><OnboardingPage /></RotaOnboarding>} />

          {/* Investidor */}
          <Route path="/dashboard" element={<RotaInvestidor><ComSidebar><DashboardPage /></ComSidebar></RotaInvestidor>} />
          <Route path="/carteira" element={<RotaInvestidor><ComSidebar><CarteiraPage /></ComSidebar></RotaInvestidor>} />
          <Route path="/simulacao" element={<RotaInvestidor><ComSidebar><SimulacaoPage /></ComSidebar></RotaInvestidor>} />
          <Route path="/mercado" element={<RotaInvestidor><ComSidebar><MercadoPage /></ComSidebar></RotaInvestidor>} />

          {/* Comum (perfil serve ambos os perfis, desde que autenticado) */}
          <Route
            path="/perfil"
            element={
              <RequerAutenticacao>
                <ComSidebar>
                  <PerfilPage />
                </ComSidebar>
              </RequerAutenticacao>
            }
          />

          {/* Administrador */}
          <Route path="/admin/dashboard" element={<RotaAdmin><ComSidebar><AdminDashboardPage /></ComSidebar></RotaAdmin>} />
          <Route path="/admin/utilizadores" element={<RotaAdmin><ComSidebar><UtilizadoresPage /></ComSidebar></RotaAdmin>} />
          <Route path="/admin/ativos" element={<RotaAdmin><ComSidebar><AtivosPage /></ComSidebar></RotaAdmin>} />
          <Route path="/admin/inflacao" element={<RotaAdmin><ComSidebar><InflacaoPage /></ComSidebar></RotaAdmin>} />
          <Route path="/admin/logs" element={<RotaAdmin><ComSidebar><LogsPage /></ComSidebar></RotaAdmin>} />
          <Route path="/admin/monitor" element={<RotaAdmin><ComSidebar><MonitorPage /></ComSidebar></RotaAdmin>} />

          <Route path="/" element={<RaizRedirect />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

function RequerAutenticacao({ children }) {
  const { user, carregando } = useAuth();
  if (carregando) return <Carregando />;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}
