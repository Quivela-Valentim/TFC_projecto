"""
Serviço de raspagem da BODIVA — RF008.

O TFC define que os dados são "recolhidos via web scraping (de forma manual)":
este módulo faz a raspagem, mas quem decide QUANDO correr e QUE dados persistir
é sempre o administrador, através do comando de gestão 'raspar_bodiva' e do
painel administrativo — nunca é executado automaticamente em segundo plano,
para manter o RN010 (só o administrador gere os dados de mercado).
"""
import logging
from datetime import date
from decimal import Decimal, InvalidOperation

import requests
from bs4 import BeautifulSoup
from django.utils import timezone

logger = logging.getLogger(__name__)

BODIVA_BASE_URL = "https://www.bodiva.ao"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
}
TIMEOUT = 15


def _to_decimal(texto: str):
    """Converte texto formatado pt-PT para Decimal (ex: '1.234,56' → 1234.56)."""
    if not texto:
        return None
    try:
        limpo = texto.strip().replace(".", "").replace(",", ".").replace("%", "").replace("AOA", "").strip()
        return Decimal(limpo)
    except InvalidOperation:
        return None


class ScraperBodiva:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def _get(self, url: str):
        try:
            resp = self.session.get(url, timeout=TIMEOUT)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except requests.RequestException as e:
            logger.error(f"[Scraper] Erro ao aceder {url}: {e}")
            return None

    def raspar_resumo_mercado(self) -> list[dict]:
        """
        Raspa a tabela de cotações da página principal da BODIVA.
        Retorna lista de dicts com os campos do modelo AtivoBodiva.

        NOTA: os seletores CSS abaixo são estimados — ajustar após inspecionar
        o HTML real de bodiva.ao com as DevTools do navegador.
        """
        soup = self._get(f"{BODIVA_BASE_URL}/mercado/cotacoes")
        if not soup:
            return []

        resultados = []
        tabela = soup.select_one("table.cotacoes, table#market-table, .market-table")
        if not tabela:
            logger.warning("[Scraper] Tabela de cotações não encontrada.")
            return []

        for linha in tabela.select("tbody tr"):
            cols = linha.select("td")
            if len(cols) < 4:
                continue
            try:
                resultados.append({
                    "ticker": cols[0].get_text(strip=True),
                    "nome": cols[1].get_text(strip=True),
                    "preco_ultimo": _to_decimal(cols[2].get_text(strip=True)),
                    "variacao_percentual": _to_decimal(cols[3].get_text(strip=True)),
                })
            except IndexError as e:
                logger.debug(f"[Scraper] Linha ignorada: {e}")

        logger.info(f"[Scraper] Cotações obtidas: {len(resultados)} ativos.")
        return resultados

    def atualizar_cotacoes_e_historico(self, data_referencia: date = None):
        """
        Raspa o mercado e grava directamente em 'resumo_mercados' — a mesma
        tabela real usada pelo motor de simulação (RF009). Não é obrigatório
        usar este scraper: se já tiveres o teu próprio processo a alimentar
        'resumo_mercados' (ex: um script à parte em MySQL), este comando é
        apenas uma alternativa opcional.

        Activos ainda não cadastrados no catálogo (AtivoBodiva) são
        ignorados aqui de propósito: a criação de novos activos é uma
        decisão do administrador (RN010), feita no painel administrativo ou
        com o comando 'sincronizar_ativos'.
        """
        from bodiva_app.models import AtivoBodiva, ResumoMercado

        data_referencia = data_referencia or timezone.localdate()
        cotacoes = self.raspar_resumo_mercado()
        atualizados = 0

        tickers_cadastrados = {
            a.ticker: a for a in AtivoBodiva.objects.filter(ativo=True)
        }
        mapa_mercado = {"ACAO": "Acções", "OT": "OT-NR", "BT": "BT"}

        for dado in cotacoes:
            ticker = dado.get("ticker")
            ativo = tickers_cadastrados.get(ticker)
            if not ativo:
                continue
            try:
                ResumoMercado.objects.update_or_create(
                    codigo=ticker, data_referencia=data_referencia,
                    defaults={
                        "mercado": mapa_mercado.get(ativo.tipo, ativo.tipo),
                        "preco": dado.get("preco_ultimo"),
                        "variacao_percentual": dado.get("variacao_percentual"),
                        "num_negocios": 0,
                    },
                )
                atualizados += 1
            except Exception as e:
                logger.error(f"[Scraper] Erro ao atualizar {ticker}: {e}")

        logger.info(f"[Scraper] Atualização concluída: {atualizados}/{len(cotacoes)} ativos.")
        return atualizados
