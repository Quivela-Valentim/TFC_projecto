"""
Geração de relatórios em PDF — RF011 (relatórios resumidos das simulações),
RF012 (exportação em PDF), CSU-004 (o investidor pode exportar a simulação),
CSU-009 (o administrador pode emitir um relatório administrativo após
consultar os logs).
"""
from io import BytesIO

from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable

AZUL_ESCURO = colors.HexColor("#0F1F3D")
AZUL_VIVO = colors.HexColor("#2B6CFF")
CINZA = colors.HexColor("#5B6472")


def _estilos():
    base = getSampleStyleSheet()
    base.add(ParagraphStyle("TituloBodiva", parent=base["Title"], textColor=AZUL_ESCURO, fontSize=18, spaceAfter=4))
    base.add(ParagraphStyle("SubtituloBodiva", parent=base["Normal"], textColor=CINZA, fontSize=10, spaceAfter=14))
    base.add(ParagraphStyle("SeccaoBodiva", parent=base["Heading2"], textColor=AZUL_ESCURO, fontSize=13, spaceBefore=14, spaceAfter=8))
    base.add(ParagraphStyle("RodapeBodiva", parent=base["Normal"], textColor=CINZA, fontSize=8, spaceBefore=18))
    return base


def _tabela(dados, larguras=None):
    tabela = Table(dados, colWidths=larguras, repeatRows=1)
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL_ESCURO),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F5FA")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D8DEE9")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return tabela


def _pct(valor):
    return f"{float(valor):+.2f}%" if valor is not None else "—"


def _aoa(valor):
    return f"{float(valor):,.2f} Kz".replace(",", " ") if valor is not None else "—"


def gerar_relatorio_simulacao(simulacao, investidor) -> bytes:
    """RF012/CSU-004 — relatório em PDF de uma simulação de investimento."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm, leftMargin=2 * cm, rightMargin=2 * cm)
    estilos = _estilos()
    elementos = []

    elementos.append(Paragraph("Kiki Simulador", estilos["TituloBodiva"]))
    elementos.append(Paragraph("Relatório de Simulação de Investimento", estilos["SubtituloBodiva"]))
    elementos.append(HRFlowable(width="100%", color=AZUL_VIVO, thickness=1.2))
    elementos.append(Spacer(1, 12))

    elementos.append(Paragraph(
        f"<b>Investidor:</b> {investidor.first_name} {investidor.last_name} ({investidor.email})<br/>"
        f"<b>Gerado em:</b> {timezone.localtime(timezone.now()).strftime('%d/%m/%Y %H:%M')}",
        estilos["Normal"],
    ))

    elementos.append(Paragraph("Parâmetros da Simulação", estilos["SeccaoBodiva"]))
    elementos.append(_tabela([
        ["Ativo", "Tipo", "Período", "Valor Investido"],
        [
            simulacao.ativo.ticker, simulacao.ativo.get_tipo_display(),
            f"{simulacao.data_inicio.strftime('%d/%m/%Y')} — {simulacao.data_fim.strftime('%d/%m/%Y')}",
            _aoa(simulacao.valor_investido),
        ],
    ]))

    elementos.append(Paragraph("Resultado da Simulação", estilos["SeccaoBodiva"]))
    elementos.append(_tabela([
        ["Indicador", "Valor"],
        ["Preço no início do período", _aoa(simulacao.preco_inicio)],
        ["Preço no fim do período", _aoa(simulacao.preco_fim)],
        ["Inflação acumulada no período (IPC)", _pct(simulacao.inflacao_acumulada_pct)],
        ["Rentabilidade nominal", _pct(simulacao.rentabilidade_nominal_pct)],
        ["Rentabilidade real (ajustada à inflação)", _pct(simulacao.rentabilidade_real_pct)],
        ["Valor final (nominal)", _aoa(simulacao.valor_final_nominal)],
        ["Valor final (real)", _aoa(simulacao.valor_final_real)],
        ["Lucro/Prejuízo nominal", _aoa(simulacao.lucro_prejuizo_nominal)],
    ], larguras=[9 * cm, 7 * cm]))

    elementos.append(Paragraph(
        "Este relatório é gerado por um simulador educacional, com base em dados históricos "
        "armazenados no sistema (RN013). Os resultados são meramente informativos e não "
        "constituem uma recomendação de investimento.",
        estilos["RodapeBodiva"],
    ))

    doc.build(elementos)
    return buffer.getvalue()


def gerar_relatorio_logs(logs, administrador, filtros_texto="") -> bytes:
    """RF012/CSU-009 — relatório administrativo em PDF, emitido após a consulta de logs."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm, leftMargin=2 * cm, rightMargin=2 * cm)
    estilos = _estilos()
    elementos = []

    elementos.append(Paragraph("Kiki Simulador", estilos["TituloBodiva"]))
    elementos.append(Paragraph("Relatório Administrativo — Logs de Auditoria", estilos["SubtituloBodiva"]))
    elementos.append(HRFlowable(width="100%", color=AZUL_VIVO, thickness=1.2))
    elementos.append(Spacer(1, 12))

    elementos.append(Paragraph(
        f"<b>Administrador:</b> {administrador.first_name or administrador.username} ({administrador.email})<br/>"
        f"<b>Gerado em:</b> {timezone.localtime(timezone.now()).strftime('%d/%m/%Y %H:%M')}<br/>"
        f"<b>Filtros aplicados:</b> {filtros_texto or 'nenhum (últimos 30 dias por defeito)'}<br/>"
        f"<b>Total de registos:</b> {len(logs)}",
        estilos["Normal"],
    ))
    elementos.append(Spacer(1, 10))

    linhas = [["Tipo", "Utilizador", "Detalhes", "IP", "Data/Hora"]]
    for log in logs:
        quem = log.utilizador.email if log.utilizador else (log.identificador_tentativa or "—")
        linhas.append([
            Paragraph(log.get_tipo_display(), estilos["Normal"]),
            Paragraph(quem, estilos["Normal"]),
            Paragraph((log.detalhes or "—")[:120], estilos["Normal"]),
            log.endereco_ip or "—",
            timezone.localtime(log.criado_em).strftime("%d/%m/%Y %H:%M"),
        ])

    elementos.append(_tabela(linhas, larguras=[2.6 * cm, 3.6 * cm, 6.5 * cm, 2.3 * cm, 2.5 * cm]))

    elementos.append(Paragraph(
        "Registo de auditoria confidencial — para uso administrativo interno. "
        "Não contém palavras-passe nem outros dados sensíveis (RNF002).",
        estilos["RodapeBodiva"],
    ))

    doc.build(elementos)
    return buffer.getvalue()
