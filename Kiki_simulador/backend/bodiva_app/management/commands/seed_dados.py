"""
Management command: python manage.py seed_dados

Já não inventa preços de ativos — os preços vêm sempre, ao vivo, das tuas
tabelas reais (resumo_mercados/livros_de_ordens). Este comando faz só três
coisas, todas seguras de repetir:

  1. Cria uma conta de administrador de demonstração (só se ainda não existir).
  2. Semeia inflação de exemplo — só se a tabela de inflação estiver
     completamente vazia, para nunca sobrepor dados reais que já tenhas inserido.
  3. Corre a sincronização do catálogo de ativos (equivalente a chamar
     'sincronizar_ativos'), para já ficares com os ativos das tuas tabelas
     reais prontos a usar.
"""
import random
from datetime import date

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import DatabaseError, transaction

from bodiva_app.models import HistoricoInflacao, Perfil, User

IPC_BASE_MENSAL = 1.6  # % mensal ilustrativo — substitui pelos valores reais do INE Angola


class Command(BaseCommand):
    help = "Cria um administrador de demonstração, semeia inflação de exemplo e sincroniza o catálogo de ativos."

    def add_arguments(self, parser):
        parser.add_argument("--meses-inflacao", type=int, default=12, help="Meses de inflação de exemplo a gerar (default: 12)")

    def handle(self, *args, **opts):
        admin_user, criado = User.objects.get_or_create(
            email="admin@bodiva-sim.ao",
            defaults={
                "username": "admin",
                "first_name": "Administrador",
                "perfil": Perfil.ADMINISTRADOR,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if criado:
            admin_user.set_password("Admin@2026")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Administrador criado: admin@bodiva-sim.ao / Admin@2026"))
        else:
            self.stdout.write("Administrador já existia, mantido.")

        if HistoricoInflacao.objects.exists():
            self.stdout.write("Já existem registos de inflação — não semeei nada, para não sobrepor dados reais.")
        else:
            self._seed_inflacao(opts["meses_inflacao"])
            self.stdout.write(self.style.SUCCESS(
                f"Inflação de exemplo criada para {opts['meses_inflacao']} meses — "
                "substitui pelos valores reais do INE Angola no painel de administrador."
            ))

        self.stdout.write("A sincronizar o catálogo de ativos a partir das tuas tabelas reais...")
        try:
            call_command("sincronizar_ativos")
        except DatabaseError as e:
            self.stdout.write(self.style.WARNING(
                "Não consegui ler 'resumo_mercados'/'livros_de_ordens' — a base de dados activa "
                "ainda não tem essas tabelas (normal se ainda não ligaste o Django à tua base MySQL "
                f"real). Detalhe: {e}"
            ))

    @transaction.atomic
    def _seed_inflacao(self, meses):
        hoje = date.today()
        random.seed(42)
        for i in range(meses, -1, -1):
            mes = hoje.month - i
            ano = hoje.year
            while mes <= 0:
                mes += 12
                ano -= 1
            ipc = round(IPC_BASE_MENSAL + random.uniform(-0.6, 0.6), 4)
            HistoricoInflacao.objects.update_or_create(
                ano=ano, mes=mes, defaults={"ipc_mensal": ipc, "fonte": "Exemplo (substituir pelo INE Angola)"},
            )
