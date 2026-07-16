from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    # ── Autenticação — RF001 ──────────────────────────────────────────────
    path("auth/registo/", views.RegistoView.as_view(), name="registo"),
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("auth/logout/", views.LogoutView.as_view(), name="logout"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/me/", views.MeView.as_view(), name="me"),
    path("auth/recuperar-password/", views.PedirRecuperacaoPasswordView.as_view(), name="pedir-recuperacao"),
    path("auth/redefinir-password/", views.ConfirmarRecuperacaoPasswordView.as_view(), name="confirmar-recuperacao"),

    # ── Carteira — RF002, RF003, RN003 ────────────────────────────────────
    path("carteira/criar/", views.CriarCarteiraView.as_view(), name="criar-carteira"),
    path("carteira/", views.CarteiraView.as_view(), name="carteira"),
    path("carteira/posicoes/", views.PosicoesView.as_view(), name="posicoes"),
    path("carteira/posicoes/<int:pk>/", views.RemoverAtivoView.as_view(), name="remover-ativo"),
    path("carteira/adicionar-ativo/", views.AdicionarAtivoView.as_view(), name="adicionar-ativo"),
    path("carteira/movimentos/", views.MovimentosView.as_view(), name="movimentos"),

    # ── Mercado — RF008, RF009 ─────────────────────────────────────────────
    path("mercado/", views.MercadoListView.as_view(), name="mercado"),
    path("mercado/inflacao/", views.InflacaoView.as_view(), name="inflacao"),
    path("mercado/<int:pk>/", views.AtivoDetalheView.as_view(), name="ativo-detalhe"),
    path("mercado/<int:pk>/historico/", views.HistoricoPrecoView.as_view(), name="ativo-historico"),

    # ── Simulações — RF004-RF007 ───────────────────────────────────────────
    path("simulacoes/simular/", views.SimularView.as_view(), name="simular"),
    path("simulacoes/", views.HistoricoSimulacoesView.as_view(), name="historico-simulacoes"),
    path("simulacoes/comparar/", views.comparar_simulacoes, name="comparar-simulacoes"),
    path("simulacoes/<int:pk>/relatorio/", views.RelatorioSimulacaoView.as_view(), name="relatorio-simulacao"),

    # ── Dashboards — CSU-005 ───────────────────────────────────────────────
    path("dashboard/investidor/", views.DashboardInvestidorView.as_view(), name="dashboard-investidor"),
    path("dashboard/admin/", views.DashboardAdminView.as_view(), name="dashboard-admin"),

    # ── Administração — RF013, RF014, RF015 ────────────────────────────────
    path("admin/utilizadores/", views.GerirUtilizadoresView.as_view(), name="admin-utilizadores"),
    path(
        "admin/utilizadores/<int:pk>/bloquear/",
        views.AlterarEstadoUtilizadorView.as_view(), {"acao": "bloquear"},
        name="admin-bloquear-utilizador",
    ),
    path(
        "admin/utilizadores/<int:pk>/desbloquear/",
        views.AlterarEstadoUtilizadorView.as_view(), {"acao": "desbloquear"},
        name="admin-desbloquear-utilizador",
    ),
    path("admin/utilizadores/<int:pk>/", views.ExcluirUtilizadorView.as_view(), name="admin-excluir-utilizador"),

    path("admin/inflacao/", views.GerirInflacaoView.as_view(), name="admin-inflacao"),
    path("admin/inflacao/<int:pk>/", views.GerirInflacaoDetalheView.as_view(), name="admin-inflacao-detalhe"),

    path("admin/ativos/", views.GerirAtivosView.as_view(), name="admin-ativos"),
    path("admin/ativos/<int:pk>/", views.GerirAtivoDetalheView.as_view(), name="admin-ativo-detalhe"),
    path("admin/ativos/<int:pk>/precos/", views.GerirPrecosHistoricosView.as_view(), name="admin-ativo-precos"),

    path("admin/logs/", views.LogsView.as_view(), name="admin-logs"),
    path("admin/logs/relatorio/", views.RelatorioLogsView.as_view(), name="admin-relatorio-logs"),
    path("admin/monitor/", views.MonitorSistemaView.as_view(), name="admin-monitor"),
]
