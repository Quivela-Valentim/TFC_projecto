"""
Management command: python manage.py sincronizar_ativos

Agora que o Django lê 'resumo_mercados' e 'livros_de_ordens' AO VIVO (ver
ResumoMercado/LivroDeOrdens em models.py), este comando só precisa de tratar
de uma coisa: garantir que existe um registo de catálogo (AtivoBodiva) para
cada código novo que apareça nessas tabelas — porque o nome comercial, o
tipo, o ISIN, a taxa de cupão e a maturidade não vêm de lá.

Corre sempre pela mesma ligação do Django (a que estiver configurada em
DATABASES), não precisa de credenciais à parte. Seguro correr quantas vezes
quiseres — nunca apaga nada, só cria o que falta e actualiza ISIN/taxa/maturidade.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from bodiva_app.models import AtivoBodiva, LivroDeOrdens, ResumoMercado, TipoAtivo


def mapear_tipo(valor):
    """
    Deduz o TipoAtivo a partir do campo 'mercado' (resumo_mercados) ou
    'tipologia' (livros_de_ordens). Devolve None para tipos fora do âmbito
    do TFC (ex: 'Obrigações Ordinárias', dívida de empresas/bancos, não do
    Tesouro) — esses códigos ficam de fora do catálogo do simulador.
    """
    if not valor:
        return None
    v = valor.strip().upper()
    if v.startswith("AC"):
        return TipoAtivo.ACAO
    if v.startswith("OT"):
        return TipoAtivo.OBRIGACAO_TESOURO
    if v.startswith("BT"):
        return TipoAtivo.BILHETE_TESOURO
    if "TESOURO" in v and "OBRIGA" in v:
        return TipoAtivo.OBRIGACAO_TESOURO
    if "BILHETE" in v:
        return TipoAtivo.BILHETE_TESOURO
    return None


class Command(BaseCommand):
    help = "Sincroniza o catálogo de ativos (AtivoBodiva) a partir de resumo_mercados/livros_de_ordens."

    def handle(self, *args, **opts):
        with transaction.atomic():
            codigos_resumo = {}  # codigo -> tipo
            ignorados_resumo = set()
            for codigo, mercado in ResumoMercado.objects.values_list("codigo", "mercado").distinct():
                tipo = mapear_tipo(mercado)
                if tipo is None:
                    ignorados_resumo.add((codigo, mercado))
                    continue
                codigos_resumo[codigo.strip()] = tipo

            criados = []
            for codigo, tipo in codigos_resumo.items():
                _, criado = AtivoBodiva.objects.get_or_create(
                    ticker=codigo, defaults={"nome": codigo, "tipo": tipo, "ativo": True},
                )
                if criado:
                    criados.append(codigo)

            # Enriquecer com ISIN / taxa de cupão / maturidade a partir do registo mais recente de cada código
            vistos = set()
            enriquecidos = 0
            ignorados_livro = set()
            for linha in LivroDeOrdens.objects.order_by("codigo", "-data_referencia"):
                codigo = linha.codigo.strip()
                if codigo in vistos:
                    continue
                vistos.add(codigo)

                tipo = mapear_tipo(linha.tipologia)
                if tipo is None:
                    ignorados_livro.add((codigo, linha.tipologia))
                    continue

                taxa = linha.taxa_de_cupao
                if taxa is not None and abs(taxa) <= 1:
                    taxa = taxa * 100  # assume fração (0.18 -> 18.00%) — confirma no painel se fizer sentido

                atualizados = AtivoBodiva.objects.filter(ticker=codigo).update(
                    isin=(linha.isin or "")[:12],
                    taxa_juro_nominal=taxa,
                    data_maturidade=linha.data_de_vencimento,
                )
                if atualizados:
                    enriquecidos += 1

        self.stdout.write(self.style.SUCCESS(
            f"Ativos novos no catálogo: {len(criados)} | Enriquecidos com ISIN/taxa/maturidade: {enriquecidos}"
        ))
        if criados:
            self.stdout.write("Novos: " + ", ".join(sorted(criados)))
        if ignorados_resumo:
            self.stdout.write(self.style.WARNING(
                "Ignorados em resumo_mercados (tipo não reconhecido): "
                + ", ".join(f"{c} ({m})" for c, m in sorted(ignorados_resumo))
            ))
        if ignorados_livro:
            self.stdout.write(self.style.WARNING(
                "Ignorados em livros_de_ordens (tipologia não reconhecida): "
                + ", ".join(f"{c} ({t})" for c, t in sorted(ignorados_livro))
            ))
        self.stdout.write(
            "Ativos novos ficam com o código como nome provisório — edita o nome "
            "comercial de cada um no painel de administrador (Dados Financeiros)."
        )
