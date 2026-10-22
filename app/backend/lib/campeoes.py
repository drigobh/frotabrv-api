"""Histórico de campeões KM/L (meses fechados) e e-mail de parabéns do dia 1º."""

import logging
import os
from html import escape

from lib.avisos import destinatarios
from lib.dates import last_months, now_iso, today_iso
from lib.db import db
from lib.email import EmailError, send_email
from lib.ranking import calcular_ranking
from models.ranking import CampeaoMes, HistoricoCampeoes, PlacarItem

logger = logging.getLogger(__name__)

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]


def mes_longo(ym: str) -> str:
    return f"{MESES[int(ym[5:7]) - 1]} de {ym[:4]}"


def _num(v: float, d: int = 2) -> str:
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def mes_anterior() -> str:
    return last_months(2)[0]


async def _meses_fechados() -> list[str]:
    primeiro = await db.abastecimentos.find_one({}, {"_id": 0, "data": 1}, sort=[("data", 1)])
    if not primeiro:
        return []
    atual = today_iso()[:7]
    out, y, m = [], int(primeiro["data"][:4]), int(primeiro["data"][5:7])
    while f"{y:04d}-{m:02d}" < atual:
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


async def campeao_do_mes(mes: str) -> CampeaoMes | None:
    r = await calcular_ranking(mes)
    if not r.itens:
        return None
    t = r.itens[0]
    vice = r.itens[1] if len(r.itens) > 1 else None
    envio = await db.parabens_envios.find_one({"mes": mes}, {"_id": 0}, sort=[("enviado_em", -1)])
    return CampeaoMes(
        mes=mes, motorista_id=t.motorista_id, motorista_nome=t.motorista_nome, media_km_l=t.media_km_l,
        km_rodados=t.km_rodados, meta_km_l=r.meta_km_l, atingiu_meta=t.atingiu_meta, participantes=len(r.itens),
        vice_nome=vice.motorista_nome if vice else None, vice_media=vice.media_km_l if vice else None, parabens=envio,
    )


async def historico() -> HistoricoCampeoes:
    meses: list[CampeaoMes] = []
    for mes in reversed(await _meses_fechados()):
        c = await campeao_do_mes(mes)
        if c:
            meses.append(c)
    placar: dict[str, PlacarItem] = {}
    for c in meses:
        p = placar.setdefault(c.motorista_id, PlacarItem(motorista_id=c.motorista_id, motorista_nome=c.motorista_nome, vitorias=0, meses=[], melhor_media=0))
        p.vitorias += 1
        p.meses.append(c.mes)
        p.melhor_media = max(p.melhor_media, c.media_km_l)
    ordem = sorted(placar.values(), key=lambda p: (-p.vitorias, -p.melhor_media))
    return HistoricoCampeoes(meses=meses, placar=ordem)


def _html(c: CampeaoMes, vitorias: int) -> tuple[str, str]:
    marca = escape(os.environ["EMAIL_FROM_NAME"])
    nome = escape(c.motorista_nome)
    primeiro_nome = escape(c.motorista_nome.split(" ")[0])
    assunto = f"Parabéns, {c.motorista_nome.split(' ')[0]}! Campeão de economia de {mes_longo(c.mes)}"
    meta = (f"Você bateu a meta da frota de {_num(c.meta_km_l)} km/L." if c.atingiu_meta
            else f"A meta da frota é {_num(c.meta_km_l)} km/L — você foi o que chegou mais perto!")
    bis = f"<p style=\"font-size:14px;color:#334155\">Este é o seu <b>{vitorias}º título</b>. Que sequência!</p>" if vitorias > 1 else ""
    vice = (f"<p style=\"font-size:13px;color:#64748B\">Vice-campeão: {escape(c.vice_nome)} ({_num(c.vice_media or 0)} km/L).</p>"
            if c.vice_nome else "")
    html = (
        '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#F1F5F9"><tr><td align="center" style="padding:24px 12px">'
        '<table role="presentation" width="560" cellspacing="0" cellpadding="0" style="max-width:560px;background:#FFFFFF;border-radius:12px">'
        '<tr><td align="center" style="background:#0B0F17;padding:28px 24px;border-radius:12px 12px 0 0;font-family:Arial,sans-serif">'
        '<div style="display:inline-block;width:84px;height:84px;line-height:84px;border-radius:42px;background:#F59E0B;font-size:42px;color:#451A03">&#127942;</div>'
        f'<p style="margin:14px 0 0;color:#FBBF24;font-size:11px;letter-spacing:2px;text-transform:uppercase">Campeão de economia · {escape(mes_longo(c.mes))}</p>'
        f'<p style="margin:6px 0 0;color:#FFFFFF;font-size:24px;font-weight:bold">{nome}</p></td></tr>'
        '<tr><td style="padding:24px;font-family:Arial,sans-serif">'
        f'<p style="font-size:15px;color:#0F172A">Parabéns, {primeiro_nome}! Você foi o motorista mais econômico da frota em {escape(mes_longo(c.mes))}.</p>'
        '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin:12px 0"><tr>'
        f'<td align="center" style="padding:12px;background:#F8FAFC;border-radius:8px"><p style="margin:0;font-size:11px;color:#64748B">MÉDIA</p><p style="margin:4px 0 0;font-size:22px;font-weight:bold;color:#0F172A">{_num(c.media_km_l)} km/L</p></td>'
        '<td width="12"></td>'
        f'<td align="center" style="padding:12px;background:#F8FAFC;border-radius:8px"><p style="margin:0;font-size:11px;color:#64748B">KM RODADOS</p><p style="margin:4px 0 0;font-size:22px;font-weight:bold;color:#0F172A">{_num(c.km_rodados, 0)}</p></td>'
        '</tr></table>'
        f'<p style="font-size:14px;color:#334155">{meta} Sua direção cuidadosa economiza combustível, reduz custos e dá exemplo para toda a equipe.</p>'
        f"{bis}{vice}"
        f'<p style="margin-top:24px;font-size:12px;color:#94A3B8">Enviado por {marca} no dia 1º de cada mês ao campeão do ranking KM/L, com cópia para a administração.</p>'
        "</td></tr></table></td></tr></table>"
    )
    return assunto, html


async def enviar_parabens(origem: str, mes: str | None = None) -> dict | None:
    mes = mes or mes_anterior()
    c = await campeao_do_mes(mes)
    if not c:
        logger.info("Parabéns %s: sem campeão (nenhum abastecimento com KM)", mes)
        return None
    mot = await db.motoristas.find_one({"id": c.motorista_id}, {"_id": 0})
    email_mot = (mot or {}).get("email") or None
    _, _, admins = await destinatarios()  # admins ativos + extras dos avisos
    para = list(dict.fromkeys(([email_mot] if email_mot else []) + admins))
    vitorias = next((p.vitorias for p in (await historico()).placar if p.motorista_id == c.motorista_id), 1)
    assunto, html = _html(c, vitorias)
    enviados, falhas = 0, []
    for email in para:
        try:
            await send_email(to=email, subject=assunto, html=html)
            enviados += 1
        except EmailError as e:
            falhas.append(f"{email}: {e}")
            if e.pausado:
                break
    registro = {"mes": mes, "enviado_em": now_iso(), "origem": origem, "motorista_email": email_mot,
                "destinatarios": para, "enviados": enviados, "falhas": falhas}
    await db.parabens_envios.insert_one(dict(registro))
    logger.info("Parabéns %s (%s): %s/%s enviados", mes, c.motorista_nome, enviados, len(para))
    return registro
