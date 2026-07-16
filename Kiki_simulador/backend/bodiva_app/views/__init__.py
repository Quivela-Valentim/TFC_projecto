from bodiva_app.views.auth import (  # noqa: F401
    ConfirmarRecuperacaoPasswordView,
    LoginView,
    LogoutView,
    MeView,
    PedirRecuperacaoPasswordView,
    RegistoView,
)
from bodiva_app.views.carteira import (  # noqa: F401
    AdicionarAtivoView,
    CarteiraView,
    CriarCarteiraView,
    MovimentosView,
    PosicoesView,
    RemoverAtivoView,
)
from bodiva_app.views.mercado import (  # noqa: F401
    AtivoDetalheView,
    HistoricoPrecoView,
    InflacaoView,
    MercadoListView,
)
from bodiva_app.views.simulacao import (  # noqa: F401
    DashboardInvestidorView,
    HistoricoSimulacoesView,
    RelatorioSimulacaoView,
    SimularView,
    comparar_simulacoes,
)
from bodiva_app.views.admin import (  # noqa: F401
    AlterarEstadoUtilizadorView,
    DashboardAdminView,
    ExcluirUtilizadorView,
    GerirAtivoDetalheView,
    GerirAtivosView,
    GerirInflacaoDetalheView,
    GerirInflacaoView,
    GerirPrecosHistoricosView,
    GerirUtilizadoresView,
    LogsView,
    MonitorSistemaView,
    RelatorioLogsView,
)
