"""
Carteira Fictícia — RF002, RF003, RN003, RN004, RN005, RN009, RN015.
"""
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from bodiva_app.models import AtivoBodiva, Carteira, MovimentoCarteira, PosicaoCarteira, TipoLog, TipoMovimento
from bodiva_app.serializers import (
    AdicionarAtivoSerializer,
    CarteiraSerializer,
    CriarCarteiraSerializer,
    MovimentoCarteiraSerializer,
    PosicaoCarteiraSerializer,
)
from bodiva_app.services.auditoria import registar_log


class CriarCarteiraView(generics.CreateAPIView):
    """POST /api/carteira/criar/ — RN003: apenas uma carteira por investidor."""
    serializer_class = CriarCarteiraSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if hasattr(request.user, "carteira"):
            return Response(
                {"detail": "Já existe uma carteira fictícia associada a esta conta. "
                           "Cada investidor pode ter apenas uma carteira."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            carteira = serializer.save()
        except IntegrityError:
            return Response(
                {"detail": "Já existe uma carteira fictícia associada a esta conta."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        registar_log(request, utilizador=request.user, tipo=TipoLog.CRIAR_CARTEIRA, detalhes=carteira.nome)
        return Response(CarteiraSerializer(carteira).data, status=status.HTTP_201_CREATED)


class CarteiraView(generics.RetrieveAPIView):
    """GET /api/carteira/ — Dados completos da carteira do investidor autenticado."""
    serializer_class = CarteiraSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Carteira, usuario=self.request.user)


class PosicoesView(generics.ListAPIView):
    """GET /api/carteira/posicoes/ — Ativos detidos na carteira (RF002)."""
    serializer_class = PosicaoCarteiraSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PosicaoCarteira.objects.filter(
            carteira__usuario=self.request.user, quantidade__gt=0
        ).select_related("ativo")


class AdicionarAtivoView(APIView):
    """
    POST /api/carteira/adicionar-ativo/
    RF002, RN004, RN005 — adiciona um ativo à carteira usando o preço
    histórico da data simulada de compra (nunca um preço arbitrário).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        carteira = get_object_or_404(Carteira, usuario=request.user)
        serializer = AdicionarAtivoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data

        ativo = get_object_or_404(AtivoBodiva, pk=dados["ativo_id"], ativo=True)
        preco = ativo.preco_em(dados["data_simulada_compra"])
        if preco is None:
            return Response(
                {"detail": f"Não existe preço histórico para {ativo.ticker} nessa data. "
                           "Peça ao administrador para completar o histórico ou escolha outra data."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        quantidade = dados["quantidade"]
        posicao, criada = PosicaoCarteira.objects.get_or_create(
            carteira=carteira, ativo=ativo,
            defaults={
                "quantidade": quantidade, "preco_medio": preco,
                "data_simulada_compra": dados["data_simulada_compra"],
            },
        )
        if not criada:
            total_anterior = posicao.quantidade * posicao.preco_medio
            total_novo = quantidade * preco
            nova_quantidade = posicao.quantidade + quantidade
            posicao.preco_medio = (total_anterior + total_novo) / nova_quantidade
            posicao.quantidade = nova_quantidade
            posicao.data_simulada_compra = dados["data_simulada_compra"]
            posicao.save()

        MovimentoCarteira.objects.create(
            carteira=carteira, ativo=ativo, tipo=TipoMovimento.ADICAO,
            quantidade=quantidade, preco_unitario=preco,
            valor_total=quantidade * preco, data_simulada=dados["data_simulada_compra"],
        )
        registar_log(
            request, utilizador=request.user, tipo=TipoLog.ADICIONAR_ATIVO,
            detalhes=f"{ativo.ticker}: {quantidade} @ {preco} AOA ({dados['data_simulada_compra']})",
        )
        return Response(PosicaoCarteiraSerializer(posicao).data, status=status.HTTP_201_CREATED)


class RemoverAtivoView(APIView):
    """DELETE /api/carteira/posicoes/<id>/ — RF003: remoção de um ativo da carteira."""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        posicao = get_object_or_404(PosicaoCarteira, pk=pk, carteira__usuario=request.user)
        ativo, quantidade = posicao.ativo, posicao.quantidade
        preco_referencia = ativo.preco_ultimo or posicao.preco_medio

        MovimentoCarteira.objects.create(
            carteira=posicao.carteira, ativo=ativo, tipo=TipoMovimento.REMOCAO,
            quantidade=quantidade, preco_unitario=preco_referencia,
            valor_total=quantidade * preco_referencia,
            data_simulada=request.data.get("data_simulada") or posicao.data_simulada_compra,
        )

        posicao.delete()
        registar_log(
            request, utilizador=request.user, tipo=TipoLog.REMOVER_ATIVO,
            detalhes=f"{ativo.ticker}: {quantidade} unidades removidas",
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class MovimentosView(generics.ListAPIView):
    """GET /api/carteira/movimentos/ — extrato de adições/remoções da carteira."""
    serializer_class = MovimentoCarteiraSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MovimentoCarteira.objects.filter(
            carteira__usuario=self.request.user
        ).select_related("ativo").order_by("-executado_em")
