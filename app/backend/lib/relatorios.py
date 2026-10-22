"""Geração de relatórios em CSV (Excel pt-BR) e PDF (A4 paisagem)."""

import csv
import io
from datetime import datetime
from zoneinfo import ZoneInfo

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

AZUL = colors.HexColor("#0B0F17")
DESTAQUE = colors.HexColor("#0EA5E9")


def br_num(v: float | None, d: int = 2) -> str:
    if v is None:
        return "—"
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def br_data(ymd: str | None) -> str:
    return "/".join(reversed(ymd[:10].split("-"))) if ymd else "—"


def gerar_csv(colunas: list[str], linhas: list[list[str]], totais: list[str] | None) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    w.writerow(colunas)
    w.writerows(linhas)
    if totais:
        w.writerow(totais)
    return ("\ufeff" + buf.getvalue()).encode("utf-8")  # BOM: Excel abre acentos corretamente


def gerar_pdf(
    titulo: str,
    periodo: str,
    usuario: str,
    colunas: list[str],
    linhas: list[list[str]],
    totais: list[str] | None,
    larguras: list[float],
) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=landscape(A4), leftMargin=12 * mm, rightMargin=12 * mm, topMargin=12 * mm, bottomMargin=14 * mm,
        title=titulo, author="Bravus Frota",
    )
    cel = ParagraphStyle("cel", fontName="Helvetica", fontSize=7.5, leading=9)
    cab = ParagraphStyle("cab", parent=cel, fontName="Helvetica-Bold", textColor=colors.white)
    h1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=AZUL)
    sub = ParagraphStyle("sub", fontName="Helvetica", fontSize=9, leading=12, textColor=colors.HexColor("#475569"))

    gerado = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M")
    data = [[Paragraph(c, cab) for c in colunas]]
    data += [[Paragraph(str(v), cel) for v in linha] for linha in linhas]
    if totais:
        data.append([Paragraph(f"<b>{v}</b>", cel) for v in totais])
    if not linhas:
        data.append([Paragraph("Nenhum registro no período.", cel)] + [""] * (len(colunas) - 1))

    largura_util = landscape(A4)[0] - 24 * mm
    soma = sum(larguras)
    tabela = Table(data, colWidths=[largura_util * w / soma for w in larguras], repeatRows=1)
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    if totais:
        estilo.append(("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E0F2FE")))
    tabela.setStyle(TableStyle(estilo))

    def rodape(canvas, d):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.drawString(12 * mm, 7 * mm, f"Bravus Frota · gerado em {gerado} por {usuario}")
        canvas.drawRightString(landscape(A4)[0] - 12 * mm, 7 * mm, f"Página {d.page}")
        canvas.setStrokeColor(DESTAQUE)
        canvas.setLineWidth(2)
        canvas.line(12 * mm, landscape(A4)[1] - 8 * mm, 60 * mm, landscape(A4)[1] - 8 * mm)
        canvas.restoreState()

    doc.build(
        [Paragraph(titulo, h1), Paragraph(f"Período: {periodo} · {len(linhas)} registro(s)", sub), Spacer(1, 6 * mm), tabela],
        onFirstPage=rodape, onLaterPages=rodape,
    )
    return buf.getvalue()
