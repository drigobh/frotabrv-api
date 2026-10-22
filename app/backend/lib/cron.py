"""Autenticação dos webhooks do cron da plataforma (Bearer WEBHOOK_CRON_SECRET) + idempotência por run_id."""

import hmac
import os

from fastapi import HTTPException, Request

from lib.dates import now_iso
from lib.db import db


async def aceitar_execucao(request: Request) -> bool:
    """Valida o cron e registra o run_id. Retorna True na primeira entrega, False se duplicada."""
    auth = request.headers.get("authorization", "")
    secret = os.environ.get("WEBHOOK_CRON_SECRET", "")
    if not secret or not auth.startswith("Bearer ") or not hmac.compare_digest(auth[7:].encode(), secret.encode()):
        raise HTTPException(status_code=401, detail="Não autorizado")
    try:
        envelope = await request.json()
    except ValueError:
        raise HTTPException(status_code=400, detail="Corpo inválido")
    run_id = request.headers.get("x-webhook-id") or (envelope or {}).get("run_id")
    if not run_id:
        raise HTTPException(status_code=400, detail="run_id ausente")
    res = await db.cron_runs.update_one(
        {"run_id": run_id}, {"$setOnInsert": {"run_id": run_id, "created_at": now_iso()}}, upsert=True
    )
    return res.upserted_id is not None
