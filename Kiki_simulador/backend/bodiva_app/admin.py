from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import (
    AtivoBodiva,
    Carteira,
    HistoricoInflacao,
    LivroDeOrdens,
    LogAuditoria,
    MovimentoCarteira,
    PosicaoCarteira,
    ResumoMercado,
    Simulacao,
    User,
)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("email", "username", "perfil", "is_active", "bloqueado_pelo_admin", "created_at")
    list_filter = ("perfil", "is_active", "bloqueado_pelo_admin")
    search_fields = ("email", "username", "first_name", "last_name")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Kiki Simulador", {
            "fields": ("perfil", "phone", "bloqueado_pelo_admin", "tentativas_login_falhadas", "bloqueado_ate")
        }),
    )


@admin.register(Carteira)
class CarteiraAdmin(admin.ModelAdmin):
    list_display = ("nome", "usuario", "criada_em")
    search_fields = ("nome", "usuario__email")


@admin.register(AtivoBodiva)
class AtivoBodivaAdmin(admin.ModelAdmin):
    list_display = ("ticker", "nome", "tipo", "preco_ultimo", "ativo", "ultima_atualizacao")
    list_filter = ("tipo", "ativo")
    search_fields = ("ticker", "nome")


@admin.register(ResumoMercado)
class ResumoMercadoAdmin(admin.ModelAdmin):
    """Tabela externa (não-gerida) — visível aqui só para consulta/depuração."""
    list_display = ("codigo", "mercado", "preco", "variacao_percentual", "data_referencia")
    list_filter = ("mercado",)
    search_fields = ("codigo",)
    date_hierarchy = "data_referencia"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(LivroDeOrdens)
class LivroDeOrdensAdmin(admin.ModelAdmin):
    """Tabela externa (não-gerida) — visível aqui só para consulta/depuração."""
    list_display = ("codigo", "tipologia", "isin", "taxa_de_cupao", "data_de_vencimento", "data_referencia")
    list_filter = ("tipologia",)
    search_fields = ("codigo", "isin")
    date_hierarchy = "data_referencia"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HistoricoInflacao)
class HistoricoInflacaoAdmin(admin.ModelAdmin):
    list_display = ("ano", "mes", "ipc_mensal", "fonte")
    list_filter = ("ano",)


@admin.register(PosicaoCarteira)
class PosicaoCarteiraAdmin(admin.ModelAdmin):
    list_display = ("carteira", "ativo", "quantidade", "preco_medio", "data_simulada_compra")


@admin.register(MovimentoCarteira)
class MovimentoCarteiraAdmin(admin.ModelAdmin):
    list_display = ("carteira", "ativo", "tipo", "quantidade", "valor_total", "executado_em")
    list_filter = ("tipo",)


@admin.register(Simulacao)
class SimulacaoAdmin(admin.ModelAdmin):
    list_display = (
        "carteira", "ativo", "valor_investido", "data_inicio", "data_fim",
        "rentabilidade_nominal_pct", "rentabilidade_real_pct", "criada_em",
    )
    list_filter = ("ativo",)


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ("tipo", "utilizador", "identificador_tentativa", "endereco_ip", "criado_em")
    list_filter = ("tipo",)
    search_fields = ("utilizador__email", "identificador_tentativa", "detalhes")
    date_hierarchy = "criado_em"
