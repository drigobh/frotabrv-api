"""Registro de auditoria: quem fez o quê, quando e de onde."""

import uuid

from fastapi import Request

from lib.dates import now_iso
from lib.db import db


async def audit(
    user: dict,
    acao: str,
    entidade: str,
    entidade_id: str | None = None,
    detalhes: str = "",
    request: Request | None = None,
) -> None:
    ip = None
    if request is not None:
        ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (
            request.client.host if request.client else None
        )
    await db.auditoria.insert_one(
        {
            "id": str(uuid.uuid4()),
            "usuario_id": user.get("id"),
            "usuario_nome": user.get("nome", "?"),
            "acao": acao,
            "entidade": entidade,
            "entidade_id": entidade_id,
            "detalhes": detalhes,
            "ip": ip,
            "created_at": now_iso(),
        }
    )
