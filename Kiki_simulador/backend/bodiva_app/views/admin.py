"""
Painel do Administrador — RF013, RF014, RF015, RN010, RN019.
CSU-005 (dashboard admin), CSU-006 (gerir utilizador), CSU-007 (consultar
dados financeiros), CSU-008 (gerir inflação), CSU-009 (consultar logs),
CSU-010 (monitorizar o sistema).
"""
from datetime import timedelta

from django.db import connection
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from bodiva_app.models import (
    AtivoBodiva,
    Carteira,
    HistoricoInflacao,
    LogAuditoria,
    ResumoMercado,
    Simulacao,
    TipoLog,
    User,
)
from bodiva_app.permissions import IsAdministrador
from bodiva_app.serializers import (
    AtivoBodivaSerializer,
    GerirUtilizadorSerializer,
    HistoricoInflacaoSerializer,
    InserirPrecoManualSerializer,
    LogAuditoriaSerializer,
    ResumoMercadoSerializer,
)
from bodiva_app.services.auditoria import registar_log
from bodiva_app.services.relatorios import gerar_relatorio_logs


# ─── CSU-006 — Gerir Utilizador ───────────────────────────────────────────────

class GerirUtilizadoresView(generics.ListAPIView):
    """GET /api/admin/utilizadores/?q=nome — lista todos os investidores registados."""
    serializer_class = GerirUtilizadorSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdministrador]

    def get_queryset(self):
        qs = User.objects.filter(perfil="INVESTIDOR").order_by("-created_at")
        termo = self.request.query_params.get("q")
        if termo:
            qs = qs.filter(email__icontains=termo) | qs.filter(username__icontains=termo)
        return qs


class AlterarEstadoUtilizadorView(APIView):
    """
    POST /api/admin/utilizadores/<pk>/bloquear/
    POST /api/admin/utilizadores/<pk>/desbloquear/
    """
    permission_classes = [permissions.IsAuthenticated, IsAdministrador]

    def post(self, request, pk, acao):
        utilizador = get_object_or_404(User, pk=pk)

        if acao == "bloquear":
            utilizador.bloqueado_pelo_admin = True
            mensagem = f"A conta de {utilizador.first_name or utilizador.email} foi bloqueada."
        elif acao == "desbloquear":
            utilizador.bloqueado_pelo_admin = False
            utilizador.limpar_tentativas_falhadas()
            mensagem = f"A conta de {utilizador.first_name or utilizador.email} foi desbloqueada."
        else:
            return Response({"detail": "Ação inválida."}, status=status.HTTP_400_BAD_REQUEST)

        utilizador.save(update_fields=["bloqueado_pelo_admin"])
        registar_log(
            request, utilizador=request.user, tipo=TipoLog.GERIR_UTILIZADOR,
            detalhes=f"{acao} — utilizador afetado: {utilizador.email}",
        )
        return Response({"detail": mensagem, "utilizador": GerirUtilizadorSerializer(utilizador).data})


class ExcluirUtilizadorView(APIView):
    """DELETE /api/admin/utilizadores/<pk>/ — o administrador não se pode excluir a si próprio."""
    permission_classes = [permissions.IsAuthenticated, IsAdministrador]

    def delete(self, request, pk):
        if str(request.user.pk) == str(pk):
            return Response(
                {"detail": "Não pode excluir a sua própria conta enquanto estiver autenticado."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        utilizador = get_object_or_404(User, pk=pk)
        email = utilizador.email
        utilizador.delete()
        registar_log(
            request, utilizador=request.user, tipo=TipoLog.GERIR_UTILIZADOR,
            detalhes=f"excluir — utilizador afetado: {email}",
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── CSU-008 — Gerir Taxa de Inflação ─────────────────────────────────────────

class GerirInflacaoView(generics.ListCreateAPIView):
    """GET/POST /api/admin/inflacao/ — RN008: um único registo por mês/ano."""
    serializer_class = HistoricoInflacaoSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdministrador]
    queryset = HistoricoInflacao.objects.order_by("-ano", "-mes")

    def create(self, request, *args, **kwargs):
        ano, mes = request.data.get("ano"), request.data.get("mes")
        if HistoricoInflacao.objects.filter(ano=ano, mes=mes).exists():
            return Response(
                {"detail": "Já existe uma taxa de inflação registada para este período."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        resposta = super().create(request, *args, **kwargs)
        registar_log(request, utilizador=request.user, tipo=TipoLog.GERIR_INFLACAO,
                     detalhes=f"inserir — {mes}/{ano}")
        return resposta


class GerirInflacaoDetalheView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/admin/inflacao/<pk>/"""
    serializer_class = HistoricoInflacaoSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdministrador]
    queryset = HistoricoInflacao.objects.all()

    def update(self, request, *args, **kwargs):
        resposta = super().update(request, *args, **kwargs)
        registar_log(request, utilizador=request.user, tipo=TipoLog.GERIR_INFLACAO,
                     detalhes=f"actualizar — registo #{kwargs['pk']}")
        return resposta

    def destroy(self, request, *args, **kwargs):
        registo = self.get_object()
        detalhes = f"eliminar — {registo.mes}/{registo.ano}"
        resposta = super().destroy(request, *args, **kwargs)
        registar_log(request, utilizador=request.user, tipo=TipoLog.GERIR_INFLACAO, detalhes=detalhes)
        return resposta


# ─── CSU-007 — Consultar Dados Financeiros / RF013 — Gerir Ativos ────────────

class GerirAtivosView(generics.ListCreateAPIView):
    """GET/POST /api/admin/ativos/"""
    serializer_class = AtivoBodivaSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdministrador]
    queryset = AtivoBodiva.objects.all().order_by("tipo", "ticker")

    def create(self, request, *args, **kwargs):
        resposta = super().create(request, *args, **kwargs)
        registar_log(request, utilizador=request.user, tipo=TipoLog.GERIR_ATIVO,
                     detalhes=f"criar ativo — {request.data.get('ticker')}")
        return resposta

    def list(self, request, *args, **kwargs):
        registar_log(request, utilizador=request.user, tipo=TipoLog.CONSULTA_DADOS_FINANCEIROS,
                     detalhes="listar ativos")
        return super().list(request, *args, **kwargs)


class GerirAtivoDetalheView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/admin/ativos/<pk>/"""
    serializer_class = AtivoBodivaSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdministrador]
    queryset = AtivoBodiva.objects.all()

    def update(self, request, *args, **kwargs):
        resposta = super().update(request, *args, **kwargs)
        registar_log(request, utilizador=request.user, tipo=TipoLog.GERIR_ATIVO,
                     detalhes=f"actualizar ativo #{kwargs['pk']}")
        return resposta


class GerirPrecosHistoricosView(generics.ListCreateAPIView):
    """
    GET/POST /api/admin/ativos/<pk>/precos/
    RN009: só inserção, dados históricos não se alteram. Escreve directamente
    em resumo_mercados — a mesma tabela real que o scraping do utilizador usa,
    para nunca haver uma cópia paralela dos dados de mercado.
    """
    serializer_class = ResumoMercadoSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdministrador]

    def _ativo(self):
        return get_object_or_404(AtivoBodiva, pk=self.kwargs["pk"])

    def get_queryset(self):
        ativo = self._ativo()
        return ResumoMercado.objects.filter(codigo=ativo.ticker).order_by("data_referencia")

    def create(self, request, *args, **kwargs):
        ativo = self._ativo()
        serializer = InserirPrecoManualSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data

        # 'mercado' e 'num_negocios' são NOT NULL em resumo_mercados mas não
        # fazem sentido para uma inserção manual — usa-se o tipo do ativo e 0.
        mercado_valor = {"ACAO": "Acções", "OT": "OT-NR", "BT": "BT"}.get(ativo.tipo, ativo.tipo)

        registo, _ = ResumoMercado.objects.update_or_create(
            codigo=ativo.ticker, data_referencia=dados["data"],
            defaults={
                "mercado": mercado_valor,
                "preco": dados["preco_fecho"],
                "variacao_percentual": dados.get("variacao_percentual"),
                "num_negocios": 0,
            },
        )
        registar_log(request, utilizador=request.user, tipo=TipoLog.GERIR_ATIVO,
                     detalhes=f"inserir preço manual — {ativo.ticker} em {dados['data']}")
        return Response(ResumoMercadoSerializer(registo).data, status=status.HTTP_201_CREATED)


# ─── CSU-009 — Consultar Logs ─────────────────────────────────────────────────

def _filtrar_logs(query_params):
    """Filtros partilhados entre a listagem (LogsView) e o relatório PDF (RelatorioLogsView)."""
    qs = LogAuditoria.objects.select_related("utilizador").order_by("-criado_em")

    inicio = query_params.get("inicio")
    fim = query_params.get("fim")
    if not inicio and not fim:
        qs = qs.filter(criado_em__gte=timezone.now() - timedelta(days=30))
    else:
        if inicio:
            qs = qs.filter(criado_em__date__gte=inicio)
        if fim:
            qs = qs.filter(criado_em__date__lte=fim)

    utilizador_id = query_params.get("utilizador")
    if utilizador_id:
        qs = qs.filter(utilizador_id=utilizador_id)

    tipo = query_params.get("tipo")
    if tipo:
        qs = qs.filter(tipo=tipo)

    partes = []
    if inicio or fim:
        partes.append(f"período {inicio or '...'} a {fim or '...'}")
    if utilizador_id:
        partes.append(f"utilizador #{utilizador_id}")
    if tipo:
        partes.append(f"tipo {tipo}")
    filtros_texto = ", ".join(partes)

    return qs, filtros_texto


class LogsView(generics.ListAPIView):
    """
    GET /api/admin/logs/?inicio=YYYY-MM-DD&fim=YYYY-MM-DD&utilizador=<id>&tipo=LOGIN
    Sem filtro de datas, assume os últimos 30 dias por defeito.
    """
    serializer_class = LogAuditoriaSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdministrador]

    def get_queryset(self):
        qs, _ = _filtrar_logs(self.request.query_params)
        return qs

    def list(self, request, *args, **kwargs):
        registar_log(request, utilizador=request.user, tipo=TipoLog.CONSULTA_LOGS)
        return super().list(request, *args, **kwargs)


class RelatorioLogsView(APIView):
    """
    GET /api/admin/logs/relatorio/?... — RF012/CSU-009: "Consulta os registos
    apresentados, podendo emitir os relatórios administrativos." Usa os
    mesmos filtros da consulta de logs.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdministrador]

    def get(self, request):
        qs, filtros_texto = _filtrar_logs(request.query_params)
        logs = list(qs[:500])  # limite de segurança para o PDF não crescer sem controlo
        pdf_bytes = gerar_relatorio_logs(logs, request.user, filtros_texto)

        registar_log(request, utilizador=request.user, tipo=TipoLog.CONSULTA_LOGS,
                     detalhes=f"emitir relatório administrativo — {filtros_texto or 'sem filtros'}")

        resposta = HttpResponse(pdf_bytes, content_type="application/pdf")
        resposta["Content-Disposition"] = 'attachment; filename="relatorio_logs.pdf"'
        return resposta


# ─── CSU-010 — Monitorar o Sistema / CSU-005 — Dashboard do Administrador ────

class MonitorSistemaView(APIView):
    """GET /api/admin/monitor/ — indicadores gerais de funcionamento do sistema."""
    permission_classes = [permissions.IsAuthenticated, IsAdministrador]

    def get(self, request):
        agora = timezone.now()

        try:
            connection.ensure_connection()
            estado_bd = "ativo"
        except Exception:
            estado_bd = "inativo"

        cutoff = agora.date() - timedelta(days=45)
        codigos_recentes = set(
            ResumoMercado.objects.filter(data_referencia__gte=cutoff).values_list("codigo", flat=True).distinct()
        )
        tickers_ativos = list(AtivoBodiva.objects.filter(ativo=True).values_list("ticker", flat=True))
        ativos_sem_preco_recente = sum(1 for t in tickers_ativos if t not in codigos_recentes)

        ultima_atualizacao = ResumoMercado.objects.order_by(
            "-data_referencia"
        ).values_list("data_referencia", flat=True).first()

        return Response({
            "estado_sistema": "operacional",
            "estado_base_dados": estado_bd,
            "total_utilizadores": User.objects.filter(perfil="INVESTIDOR").count(),
            "utilizadores_ativos": User.objects.filter(
                perfil="INVESTIDOR", bloqueado_pelo_admin=False
            ).count(),
            "utilizadores_bloqueados": User.objects.filter(bloqueado_pelo_admin=True).count(),
            "total_simulacoes": Simulacao.objects.count(),
            "total_carteiras": Carteira.objects.count(),
            "quantidade_taxas_inflacao": HistoricoInflacao.objects.count(),
            "ultima_atualizacao_dados": ultima_atualizacao,
            "ativos_com_dados_em_falta": ativos_sem_preco_recente,
        })


class DashboardAdminView(APIView):
    """GET /api/dashboard/admin/ — CSU-005: resumo para o painel do administrador."""
    permission_classes = [permissions.IsAuthenticated, IsAdministrador]

    def get(self, request):
        return Response({
            "total_utilizadores": User.objects.filter(perfil="INVESTIDOR").count(),
            "utilizadores_ativos": User.objects.filter(
                perfil="INVESTIDOR", bloqueado_pelo_admin=False
            ).count(),
            "utilizadores_bloqueados": User.objects.filter(bloqueado_pelo_admin=True).count(),
            "total_simulacoes": Simulacao.objects.count(),
            "simulacoes_recentes": list(
                Simulacao.objects.select_related("ativo", "carteira__usuario")
                .order_by("-criada_em")[:10]
                .values(
                    "id", "ativo__ticker", "carteira__usuario__email",
                    "rentabilidade_nominal_pct", "rentabilidade_real_pct", "criada_em",
                )
            ),
            "tentativas_login_falhadas_recentes": LogAuditoria.objects.filter(
                tipo=TipoLog.LOGIN_FALHADO, criado_em__gte=timezone.now() - timedelta(days=1)
            ).count(),
        })
