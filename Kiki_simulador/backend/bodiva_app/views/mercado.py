"""
Mercado — RF008, RF009, RF010 (consulta pelo investidor), lido ao vivo da
tabela real 'resumo_mercados', nunca de uma cópia.
"""
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound

from bodiva_app.models import AtivoBodiva, HistoricoInflacao, ResumoMercado
from bodiva_app.serializers import AtivoBodivaSerializer, HistoricoInflacaoSerializer, ResumoMercadoSerializer


class MercadoListView(generics.ListAPIView):
    """GET /api/mercado/?tipo=ACAO — Catálogo de ativos disponíveis para simulação (RN005)."""
    serializer_class = AtivoBodivaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        tipo = self.request.query_params.get("tipo")
        qs = AtivoBodiva.objects.filter(ativo=True)
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs.order_by("tipo", "ticker")


class AtivoDetalheView(generics.RetrieveAPIView):
    """GET /api/mercado/<pk>/ — Detalhe de um ativo."""
    serializer_class = AtivoBodivaSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = AtivoBodiva.objects.filter(ativo=True)


class HistoricoPrecoView(generics.ListAPIView):
    """GET /api/mercado/<pk>/historico/ — Série histórica de preços (para gráfico de evolução, RF010)."""
    serializer_class = ResumoMercadoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            ativo = AtivoBodiva.objects.get(pk=self.kwargs["pk"])
        except AtivoBodiva.DoesNotExist:
            raise NotFound("Ativo não encontrado.")
        return ResumoMercado.objects.filter(codigo=ativo.ticker).order_by("data_referencia")


class InflacaoView(generics.ListAPIView):
    """GET /api/mercado/inflacao/ — Dados históricos de inflação (consulta, RN009: só leitura)."""
    serializer_class = HistoricoInflacaoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HistoricoInflacao.objects.order_by("-ano", "-mes")[:36]
