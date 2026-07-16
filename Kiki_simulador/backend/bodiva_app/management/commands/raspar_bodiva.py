"""
Management command: python manage.py raspar_bodiva

Uso manual pelo administrador (RF008: "recolhidos via web scraping, de forma
manual"). Não é agendado automaticamente.
"""
from django.core.management.base import BaseCommand

from bodiva_app.services.scraper_bodiva import ScraperBodiva


class Command(BaseCommand):
    help = "Raspa cotações da BODIVA e regista um ponto no histórico de preços para hoje."

    def handle(self, *args, **options):
        scraper = ScraperBodiva()
        self.stdout.write("A raspar cotações do mercado BODIVA...")
        total = scraper.atualizar_cotacoes_e_historico()
        self.stdout.write(self.style.SUCCESS(f"Concluído. {total} ativos atualizados."))
