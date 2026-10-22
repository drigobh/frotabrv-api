"""Cálculo do ranking KM/L (compartilhado por /ranking e pelo selo do dashboard)."""

from collections import defaultdict

from lib.db import db
from models.ranking import Ranking, RankingItem

META_PADRAO = 2.5


async def get_meta() -> float:
    cfg = await db.config.find_one({"chave": "meta_km_l"}, {"_id": 0})
    return float(cfg["valor"]) if cfg else META_PADRAO


async def calcular_ranking(mes: str) -> Ranking:
    meta = await get_meta()
    abast = await db.abastecimentos.find(
        {"data": {"$regex": f"^{mes}"}, "motorista_id": {"$ne": None}, "km_rodados": {"$ne": None}}, {"_id": 0}
    ).to_list(20000)
    acc: dict[str, dict] = defaultdict(lambda: {"n": 0, "litros": 0.0, "km": 0.0, "nome": ""})
    for a in abast:
        x = acc[a["motorista_id"]]
        x["n"] += 1
        x["litros"] += a["litros"]
        x["km"] += a["km_rodados"]
        x["nome"] = a.get("motorista_label") or "?"
    linhas = sorted(
        ((mid, x, x["km"] / x["litros"]) for mid, x in acc.items() if x["litros"] > 0),
        key=lambda t: t[2], reverse=True,
    )
    itens = [
        RankingItem(
            posicao=i + 1, motorista_id=mid, motorista_nome=x["nome"], abastecimentos=x["n"],
            litros=round(x["litros"], 1), km_rodados=round(x["km"], 1), media_km_l=round(media, 2),
            percentual_meta=round(media / meta * 100, 1), atingiu_meta=media >= meta,
        )
        for i, (mid, x, media) in enumerate(linhas)
    ]
    tl = sum(x["litros"] for _, x, _ in linhas)
    media_frota = round(sum(x["km"] for _, x, _ in linhas) / tl, 2) if tl else None
    return Ranking(mes=mes, meta_km_l=meta, media_frota=media_frota, itens=itens)
