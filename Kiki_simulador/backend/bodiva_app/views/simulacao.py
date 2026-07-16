"""
Simulação de Investimento — RF004, RF005, RF006, RF007, RN006-RN013.
"""
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from bodiva_app.models import AtivoBodiva, Carteira, Simulacao, TipoLog
from bodiva_app.permissions import IsInvestidor
from bodiva_app.serializers import CarteiraSerializer, SimulacaoInputSerializer, SimulacaoSerializer
from bodiva_app.services.auditoria import registar_log
from bodiva_app.services.motor_financeiro import DadosInsuficientesError, MotorFinanceiro
from bodiva_app.services.relatorios import gerar_relatorio_simulacao


class SimularView(APIView):
    """
    POST /api/simulacoes/simular/
    { "ativo_id": 1, "valor_investido": "50000.00", "data_inicio": "2023-01-01", "data_fim": "2024-01-01" }

    RF004/RF005/RF006: calcula rentabilidade nominal e real ajustada à
    inflação para o período pedido, e guarda o resultado no histórico do
    investidor (RN012), sem alterar saldos ou posições reais.
    """
    permission_classes = [permissions.IsAuthenticated, IsInvestidor]

    def post(self, request):
        carteira = get_object_or_404(Carteira, usuario=request.user)

        if not carteira.posicoes.filter(quantidade__gt=0).exists():
            return Response(
                {"detail": "A carteira ainda não contém nenhum ativo. Adicione pelo menos um "
                           "ativo à carteira antes de simular um investimento."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SimulacaoInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data

        posicao = carteira.posicoes.filter(ativo_id=dados["ativo_id"], quantidade__gt=0).select_related("ativo").first()
        if not posicao:
            return Response(
                {"detail": "Só pode simular investimentos com ativos que já estejam na sua carteira "
                           "(CSU-004). Adicione o ativo à carteira antes de o simular."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ativo = posicao.ativo
        motor = MotorFinanceiro()

        try:
            resultado = motor.simular(
                ativo=ativo,
                valor_investido=dados["valor_investido"],
                data_inicio=dados["data_inicio"],
                data_fim=dados["data_fim"],
            )
        except DadosInsuficientesError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        simulacao = Simulacao.objects.create(
            carteira=carteira, ativo=ativo,
            valor_investido=resultado.valor_investido,
            data_inicio=dados["data_inicio"], data_fim=dados["data_fim"],
            preco_inicio=resultado.preco_inicio, preco_fim=resultado.preco_fim,
            rentabilidade_nominal_pct=resultado.rentabilidade_nominal_pct,
            inflacao_acumulada_pct=resultado.inflacao_acumulada_pct,
            rentabilidade_real_pct=resultado.rentabilidade_real_pct,
            valor_final_nominal=resultado.valor_final_nominal,
            valor_final_real=resultado.valor_final_real,
            lucro_prejuizo_nominal=resultado.lucro_prejuizo_nominal,
        )

        registar_log(
            request, utilizador=request.user, tipo=TipoLog.SIMULACAO,
            detalhes=(
                f"{ativo.ticker} | {dados['valor_investido']} AOA | "
                f"{dados['data_inicio']}→{dados['data_fim']} | "
                f"Nominal {resultado.rentabilidade_nominal_pct}% | Real {resultado.rentabilidade_real_pct}%"
            ),
        )

        return Response(SimulacaoSerializer(simulacao).data, status=status.HTTP_201_CREATED)


class HistoricoSimulacoesView(generics.ListAPIView):
    """GET /api/simulacoes/ — Histórico de simulações do investidor (RN012)."""
    serializer_class = SimulacaoSerializer
    permission_classes = [permissions.IsAuthenticated, IsInvestidor]

    def get_queryset(self):
        return Simulacao.objects.filter(
            carteira__usuario=self.request.user
        ).select_related("ativo").order_by("-criada_em")


class RelatorioSimulacaoView(APIView):
    """
    GET /api/simulacoes/<pk>/relatorio/ — RF012/CSU-004: exporta a simulação
    em PDF ("o histórico de simulação (...) podendo ser exportado pelo investidor").
    """
    permission_classes = [permissions.IsAuthenticated, IsInvestidor]

    def get(self, request, pk):
        simulacao = get_object_or_404(
            Simulacao.objects.select_related("ativo"), pk=pk, carteira__usuario=request.user
        )
        pdf_bytes = gerar_relatorio_simulacao(simulacao, request.user)

        registar_log(
            request, utilizador=request.user, tipo=TipoLog.SIMULACAO,
            detalhes=f"exportar relatório PDF — simulação #{simulacao.id} ({simulacao.ativo.ticker})",
        )

        resposta = HttpResponse(pdf_bytes, content_type="application/pdf")
        resposta["Content-Disposition"] = (
            f'attachment; filename="simulacao_{simulacao.ativo.ticker}_{simulacao.id}.pdf"'
        )
        return resposta


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated, IsInvestidor])
def comparar_simulacoes(request):
    """
    GET /api/simulacoes/comparar/?ids=1,2,3
    RF007/RN011 — compara diferentes cenários de investimento já simulados,
    usando os mesmos critérios (mesmas simulações persistidas).
    """
    ids_param = request.query_params.get("ids", "")
    ids = [i for i in ids_param.split(",") if i.strip().isdigit()]
    if len(ids) < 2:
        return Response(
            {"detail": "Indique pelo menos duas simulações para comparar (ex: ?ids=1,2)."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    simulacoes = Simulacao.objects.filter(
        id__in=ids, carteira__usuario=request.user
    ).select_related("ativo")
    return Response(SimulacaoSerializer(simulacoes, many=True).data)


class DashboardInvestidorView(APIView):
    """
    GET /api/dashboard/investidor/ — CSU-005: resumo da carteira do investidor.
    Total investido, valor atual, rentabilidade nominal e real gerais, nº de simulações.
    """
    permission_classes = [permissions.IsAuthenticated, IsInvestidor]

    def get(self, request):
        if not hasattr(request.user, "carteira"):
            return Response({"tem_carteira": False})

        carteira = request.user.carteira
        valor_investido = carteira.valor_investido
        valor_atual = carteira.valor_atual

        if valor_investido > 0:
            rentabilidade_nominal_geral = ((valor_atual - valor_investido) / valor_investido) * 100
        else:
            rentabilidade_nominal_geral = 0

        rentabilidade_real_geral, posicoes_excluidas = self._rentabilidade_real_geral(carteira)

        ultimas_simulacoes = carteira.simulacoes.select_related("ativo").order_by("-criada_em")[:5]

        return Response({
            "tem_carteira": True,
            "carteira": CarteiraSerializer(carteira).data,
            "rentabilidade_nominal_geral_pct": round(float(rentabilidade_nominal_geral), 4),
            "rentabilidade_real_geral_pct": rentabilidade_real_geral,
            "posicoes_sem_inflacao_suficiente": posicoes_excluidas,
            "numero_simulacoes": carteira.numero_simulacoes,
            "ultimas_simulacoes": SimulacaoSerializer(ultimas_simulacoes, many=True).data,
        })

    @staticmethod
    def _rentabilidade_real_geral(carteira):
        """
        CSU-005 — rentabilidade real geral da carteira: média das rentabilidades
        reais de cada posição (RN007), ponderada pelo custo de aquisição.
        Posições sem inflação registada para o seu período são excluídas do
        cálculo (e reportadas), em vez de bloquear todo o dashboard.
        """
        from datetime import date as date_cls

        motor = MotorFinanceiro()
        soma_ponderada = 0
        peso_total = 0
        excluidas = []

        for posicao in carteira.posicoes.filter(quantidade__gt=0).select_related("ativo"):
            preco_atual = posicao.ativo.preco_ultimo or posicao.preco_medio
            try:
                nominal_pct = motor.calcular_rentabilidade_nominal(posicao.preco_medio, preco_atual)
                inflacao_pct, _ = motor.calcular_inflacao_acumulada(posicao.data_simulada_compra, date_cls.today())
                real_pct = motor.calcular_rentabilidade_real(nominal_pct, inflacao_pct)
            except DadosInsuficientesError:
                excluidas.append(posicao.ativo.ticker)
                continue

            peso = float(posicao.custo_total)
            soma_ponderada += float(real_pct) * peso
            peso_total += peso

        if peso_total == 0:
            return None, excluidas
        return round(soma_ponderada / peso_total, 4), excluidas
