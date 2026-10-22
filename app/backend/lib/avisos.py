"""Resumo semanal de vencimentos (documentos, CNH e contas nos próximos 30 dias) e seu e-mail."""

import logging
import os
import uuid
from datetime import date, timedelta
from html import escape

from lib.dates import now_iso, today_iso
from lib.db import db
from lib.email import EmailError, send_email
from lib.vencimentos import ALERTA_DIAS, dias_para
from models.avisos import AvisoItem, AvisoResumo

logger = logging.getLogger(__name__)


def _br(ymd: str) -> str:
    return "/".join(reversed(ymd.split("-")))


def _brl(v: float) -> str:
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


async def montar_resumo() -> AvisoResumo:
    hoje = today_iso()
    ate = (date.fromisoformat(hoje) + timedelta(days=ALERTA_DIAS)).isoformat()
    v_ativos = {v["id"] for v in await db.veiculos.find({"ativo": True}, {"_id": 0, "id": 1}).to_list(5000)}
    motoristas = await db.motoristas.find({"ativo": True}, {"_id": 0}).to_list(5000)
    m_ativos = {m["id"] for m in motoristas}

    docs: list[AvisoItem] = []
    for d in await db.documentos.find({"validade": {"$lte": ate}}, {"_id": 0}).to_list(2000):
        if d["entidade_id"] in v_ativos | m_ativos:
            docs.append(AvisoItem(categoria="documento", titulo=f"{d['tipo']} · {d['entidade_label'].split(' · ')[0]}",
                                  detalhe=d.get("numero") or "", data=d["validade"], dias=dias_para(d["validade"], hoje)))
    for m in motoristas:
        if m.get("validade_cnh") and m["validade_cnh"] <= ate:
            docs.append(AvisoItem(categoria="cnh", titulo=f"CNH · {m['nome']}", detalhe=m.get("cnh", ""),
                                  data=m["validade_cnh"], dias=dias_para(m["validade_cnh"], hoje)))
    docs.sort(key=lambda i: i.data)

    contas = await db.contas.find({"status": "aberta", "vencimento": {"$lte": ate}}, {"_id": 0}).sort("vencimento", 1).to_list(5000)

    def item(c: dict) -> AvisoItem:
        return AvisoItem(categoria=c["tipo"], titulo=c["descricao"], detalhe=c.get("veiculo_label") or c.get("categoria", ""),
                         data=c["vencimento"], dias=dias_para(c["vencimento"], hoje), valor=c["valor"])

    pagar = [item(c) for c in contas if c["tipo"] == "pagar"]
    receber = [item(c) for c in contas if c["tipo"] == "receber"]
    return AvisoResumo(
        gerado_em=now_iso(), ate=ate, documentos=docs, contas_pagar=pagar, contas_receber=receber,
        total_pagar=round(sum(i.valor or 0 for i in pagar), 2), total_receber=round(sum(i.valor or 0 for i in receber), 2),
    )


async def destinatarios() -> tuple[list[str], list[str], list[str]]:
    """(admins ativos, extras definidos pelo admin, união sem duplicatas)."""
    admins = [u["email"] for u in await db.usuarios.find({"perfil": "admin", "ativo": True}, {"_id": 0, "email": 1}).to_list(100)]
    cfg = await db.config.find_one({"chave": "avisos_emails"}, {"_id": 0})
    extras = list(cfg["valor"]) if cfg else []
    todos = list(dict.fromkeys(e.lower() for e in admins + extras))
    return admins, extras, todos


def _prazo(i: AvisoItem) -> str:
    if i.dias < 0:
        return f'<span style="color:#DC2626;font-weight:bold">vencido há {-i.dias} d</span>'
    if i.dias == 0:
        return '<span style="color:#D97706;font-weight:bold">vence hoje</span>'
    return f'<span style="color:#D97706">em {i.dias} d</span>'


def _tabela(titulo: str, itens: list[AvisoItem], com_valor: bool, total: float | None = None) -> str:
    base_th = "text-align:left;padding:6px 8px;font-size:11px;color:#64748B;text-transform:uppercase;border-bottom:1px solid #E2E8F0"
    base_td = "padding:7px 8px;font-size:13px;color:#0F172A;border-bottom:1px solid #F1F5F9"
    th = f'style="{base_th}"'
    td = f'style="{base_td}"'
    td_dir = f'style="{base_td};text-align:right"'
    th_dir = f'style="{base_th};text-align:right"'
    colunas = 4 if com_valor else 3
    if not itens:
        corpo = (f'<tr><td colspan="{colunas}" style="padding:10px 8px;color:#64748B;font-size:13px">'
                 f"Nada vencendo nos próximos {ALERTA_DIAS} dias.</td></tr>")
    else:
        linhas = []
        for i in itens:
            valor = f"<td {td_dir}>{_brl(i.valor or 0)}</td>" if com_valor else ""
            sub = f'<br><span style="color:#64748B;font-size:11px">{escape(i.detalhe)}</span>' if i.detalhe else ""
            linhas.append(f"<tr><td {td}>{escape(i.titulo)}{sub}</td><td {td}>{_br(i.data)}</td><td {td}>{_prazo(i)}</td>{valor}</tr>")
        corpo = "".join(linhas)
    rodape = ""
    if com_valor and itens and total is not None:
        rodape = (f'<tr><td colspan="3" style="padding:8px;font-size:13px;font-weight:bold">Total</td>'
                  f'<td style="padding:8px;font-size:13px;font-weight:bold;text-align:right">{_brl(total)}</td></tr>')
    cab_valor = f"<th {th_dir}>Valor</th>" if com_valor else ""
    return (
        f'<h2 style="font-size:16px;color:#0B0F17;margin:24px 0 8px">{escape(titulo)} ({len(itens)})</h2>'
        f'<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse">'
        f"<tr><th {th}>Item</th><th {th}>Data</th><th {th}>Prazo</th>{cab_valor}</tr>"
        f"{corpo}{rodape}</table>"
    )


def montar_html(r: AvisoResumo) -> tuple[str, str]:
    marca = escape(os.environ["EMAIL_FROM_NAME"])
    vencidos = sum(1 for i in r.documentos + r.contas_pagar + r.contas_receber if i.dias < 0)
    assunto = f"{os.environ['EMAIL_FROM_NAME']} · Vencimentos da semana"
    if vencidos:
        assunto += f" ({vencidos} já vencido(s))"
    html = (
        '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#F1F5F9"><tr><td align="center" style="padding:24px 12px">'
        '<table role="presentation" width="640" cellspacing="0" cellpadding="0" style="max-width:640px;background:#FFFFFF;border-radius:12px">'
        f'<tr><td style="background:#0B0F17;padding:20px 24px;border-radius:12px 12px 0 0;font-family:Arial,sans-serif">'
        f'<p style="margin:0;color:#38BDF8;font-size:11px;letter-spacing:2px;text-transform:uppercase">Aviso semanal</p>'
        f'<p style="margin:6px 0 0;color:#FFFFFF;font-size:22px;font-weight:bold">Vencimentos até {_br(r.ate)}</p></td></tr>'
        '<tr><td style="padding:8px 24px 24px;font-family:Arial,sans-serif">'
        f'<p style="font-size:14px;color:#334155">Resumo dos documentos e contas que vencem nos próximos {ALERTA_DIAS} dias, incluindo os já vencidos. '
        f"A pagar: <b>{_brl(r.total_pagar)}</b> · A receber: <b>{_brl(r.total_receber)}</b>.</p>"
        + _tabela("Documentos e CNH", r.documentos, False)
        + _tabela("Contas a pagar", r.contas_pagar, True, r.total_pagar)
        + _tabela("Contas a receber", r.contas_receber, True, r.total_receber)
        + f'<p style="margin-top:24px;font-size:12px;color:#94A3B8">Enviado automaticamente por {marca} toda segunda-feira às 7h. '
        f"Para ajustar os destinatários, acesse o menu Avisos no sistema. Nunca pedimos senhas ou códigos por e-mail.</p>"
        "</td></tr></table></td></tr></table>"
    )
    return assunto, html


async def enviar_resumo(origem: str, usuario: str | None = None) -> dict:
    resumo = await montar_resumo()
    assunto, html = montar_html(resumo)
    _, _, para = await destinatarios()
    enviados, falhas = 0, []
    for email in para:
        try:
            await send_email(to=email, subject=assunto, html=html)
            enviados += 1
        except EmailError as e:
            falhas.append(f"{email}: {e}")
            if e.pausado:
                break
    registro = {
        "id": str(uuid.uuid4()), "origem": origem, "enviado_em": now_iso(), "destinatarios": para, "enviados": enviados,
        "falhas": falhas, "itens": len(resumo.documentos) + len(resumo.contas_pagar) + len(resumo.contas_receber), "usuario": usuario,
    }
    await db.avisos_envios.insert_one(dict(registro))
    logger.info("Resumo de vencimentos (%s): %s/%s enviados", origem, enviados, len(para))
    return registro
