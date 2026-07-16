"""
Motor Financeiro — Simulação histórica de investimento (RF004, RF005, RF006).

Regras implementadas (ver TFC — Regras de Negócio):
  RN004 — valor de investimento = quantidade * preço de compra (na data simulada)
  RN006 — Rentabilidade Nominal = (preço final - preço inicial) / preço inicial
  RN007 — Rentabilidade Real = ((1 + Rentabilidade Nominal) / (1 + Inflação Acumulada)) - 1
  RN008 — a inflação acumulada usa o IPC de cada mês do período; se faltar um único
           mês, o cálculo é interrompido com um aviso claro (não se aproxima nem ignora).
"""
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal


class DadosInsuficientesError(Exception):
    """Levantado quando faltam preços históricos ou inflação para o período pedido."""


def _meses_do_periodo(data_inicio: date, data_fim: date) -> list[tuple[int, int]]:
    """Lista (ano, mês) de cada mês entre data_inicio e data_fim, inclusive."""
    meses = []
    ano, mes = data_inicio.year, data_inicio.month
    while (ano, mes) <= (data_fim.year, data_fim.month):
        meses.append((ano, mes))
        mes += 1
        if mes > 12:
            mes = 1
            ano += 1
    return meses


@dataclass
class ResultadoSimulacao:
    valor_investido: Decimal
    preco_inicio: Decimal
    preco_fim: Decimal
    rentabilidade_nominal_pct: Decimal
    inflacao_acumulada_pct: Decimal
    rentabilidade_real_pct: Decimal
    valor_final_nominal: Decimal
    valor_final_real: Decimal
    lucro_prejuizo_nominal: Decimal
    meses_utilizados: list


class MotorFinanceiro:

    def calcular_inflacao_acumulada(self, data_inicio: date, data_fim: date):
        """
        RN008 — Inflação acumulada do período, por capitalização composta dos
        IPC mensais. Interrompe com DadosInsuficientesError se faltar um mês.
        """
        from bodiva_app.models import HistoricoInflacao

        meses = _meses_do_periodo(data_inicio, data_fim)
        fator = Decimal("1")
        em_falta = []

        registos = {
            (r.ano, r.mes): r.ipc_mensal
            for r in HistoricoInflacao.objects.filter(
                ano__gte=data_inicio.year, ano__lte=data_fim.year
            )
        }

        for ano, mes in meses:
            ipc = registos.get((ano, mes))
            if ipc is None:
                em_falta.append(f"{mes:02d}/{ano}")
                continue
            fator *= (1 + (ipc / Decimal("100")))

        if em_falta:
            raise DadosInsuficientesError(
                "Não é possível calcular a rentabilidade real: falta o índice de "
                f"inflação dos seguintes meses: {', '.join(em_falta)}. Peça ao "
                "administrador para inserir esses registos antes de simular este período."
            )

        acumulada_pct = (fator - 1) * Decimal("100")
        return acumulada_pct.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP), meses

    def calcular_rentabilidade_nominal(self, preco_inicio: Decimal, preco_fim: Decimal) -> Decimal:
        """RN006 — variação percentual do preço do activo no período."""
        if preco_inicio == 0:
            raise DadosInsuficientesError("Preço inicial inválido (zero) para o activo neste período.")
        nominal = ((preco_fim - preco_inicio) / preco_inicio) * Decimal("100")
        return nominal.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

    def calcular_rentabilidade_real(
        self, rentabilidade_nominal_pct: Decimal, inflacao_acumulada_pct: Decimal
    ) -> Decimal:
        """RN007 — Fórmula de Fisher: Real = ((1+Nominal)/(1+Inflação)) - 1."""
        rn = rentabilidade_nominal_pct / Decimal("100")
        ri = inflacao_acumulada_pct / Decimal("100")
        if (1 + ri) == 0:
            raise DadosInsuficientesError("Inflação acumulada inválida para este período.")
        real = ((1 + rn) / (1 + ri)) - 1
        return (real * Decimal("100")).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

    def simular(self, ativo, valor_investido: Decimal, data_inicio: date, data_fim: date) -> ResultadoSimulacao:
        """
        Executa a simulação completa para um activo, montante e período.
        Não persiste nada — quem chama decide se guarda o resultado (RF006:
        permite múltiplas simulações sem alterar dados reais).
        """
        if data_inicio >= data_fim:
            raise DadosInsuficientesError("A data de início deve ser anterior à data de fim.")
        if data_fim > date.today():
            raise DadosInsuficientesError("A data de fim não pode ser uma data futura (dados históricos).")
        if valor_investido <= 0:
            raise DadosInsuficientesError("O valor a investir deve ser superior a zero.")

        preco_inicio = ativo.preco_em(data_inicio)
        preco_fim = ativo.preco_em(data_fim)

        if preco_inicio is None or preco_fim is None:
            raise DadosInsuficientesError(
                f"Não existem dados históricos de preço para {ativo.ticker} "
                "numa das datas seleccionadas. Peça ao administrador para completar o histórico."
            )

        inflacao_acumulada_pct, meses = self.calcular_inflacao_acumulada(data_inicio, data_fim)
        rentabilidade_nominal_pct = self.calcular_rentabilidade_nominal(preco_inicio, preco_fim)
        rentabilidade_real_pct = self.calcular_rentabilidade_real(
            rentabilidade_nominal_pct, inflacao_acumulada_pct
        )

        valor_final_nominal = (
            valor_investido * (1 + rentabilidade_nominal_pct / Decimal("100"))
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        valor_final_real = (
            valor_investido * (1 + rentabilidade_real_pct / Decimal("100"))
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        lucro_prejuizo_nominal = valor_final_nominal - valor_investido

        return ResultadoSimulacao(
            valor_investido=valor_investido,
            preco_inicio=preco_inicio,
            preco_fim=preco_fim,
            rentabilidade_nominal_pct=rentabilidade_nominal_pct,
            inflacao_acumulada_pct=inflacao_acumulada_pct,
            rentabilidade_real_pct=rentabilidade_real_pct,
            valor_final_nominal=valor_final_nominal,
            valor_final_real=valor_final_real,
            lucro_prejuizo_nominal=lucro_prejuizo_nominal,
            meses_utilizados=meses,
        )
