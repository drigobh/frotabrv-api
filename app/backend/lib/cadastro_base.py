"""Fábrica de rotas para cadastros simples (veículos, carretas, motoristas).

Cada cadastro tem seu próprio arquivo em routers/ que só declara a configuração;
a lógica comum (listar, criar, editar inline, inativar/reativar) vive aqui uma vez.
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from lib.audit import audit
from lib.dates import now_iso
from lib.db import db
from lib.security import require


class StatusUpdate(BaseModel):
    ativo: bool


async def ids_em_uso(campo: str) -> set[str]:
    """Ids (veiculo_id/carreta_id/motorista_id) presentes em acoplamentos ativos."""
    vals = await db.acoplamentos.distinct(campo, {"status": "ativo"})
    return {v for v in vals if v}


def build_cadastro_router(
    *,
    prefix: str,
    collection: str,
    entidade: str,
    create_model: type[BaseModel],
    out_model: type[BaseModel],
    unique_field: str,
    unique_label: str,
    acop_field: str,
    sort_field: str,
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=[entidade])
    coll = db[collection]

    def _out(doc: dict, em_uso: set[str]) -> Any:
        return out_model(**doc, acoplado=doc["id"] in em_uso)

    async def _get(item_id: str) -> dict:
        doc = await coll.find_one({"id": item_id}, {"_id": 0})
        if not doc:
            raise HTTPException(status_code=404, detail=f"{entidade} não encontrado")
        return doc

    @router.get("", response_model=list[out_model])  # type: ignore[valid-type]
    async def listar(inativos: bool = False, _u: dict = Depends(require("read"))):
        query = {} if inativos else {"ativo": True}
        docs = await coll.find(query, {"_id": 0}).sort(sort_field, 1).to_list(5000)
        em_uso = await ids_em_uso(acop_field)
        return [_out(d, em_uso) for d in docs]

    @router.post("", response_model=out_model, status_code=201)
    async def criar(body: create_model, request: Request, user: dict = Depends(require("write"))):  # type: ignore[valid-type]
        data = body.model_dump()
        if await coll.find_one({unique_field: data[unique_field]}):
            raise HTTPException(status_code=409, detail=f"{unique_label} já cadastrado(a)")
        doc = {"id": str(uuid.uuid4()), **data, "ativo": True, "created_at": now_iso(), "created_by": user["nome"]}
        await coll.insert_one(dict(doc))
        await audit(user, "criar", collection, doc["id"], f"{unique_label}: {data[unique_field]}", request)
        return _out(doc, set())

    @router.put("/{item_id}", response_model=out_model)
    async def editar(item_id: str, body: create_model, request: Request, user: dict = Depends(require("write"))):  # type: ignore[valid-type]
        atual = await _get(item_id)
        data = body.model_dump()
        if await coll.find_one({unique_field: data[unique_field], "id": {"$ne": item_id}}):
            raise HTTPException(status_code=409, detail=f"{unique_label} já cadastrado(a)")
        mudancas = [f"{k}: {atual.get(k)!s} → {v!s}" for k, v in data.items() if atual.get(k) != v]
        await coll.update_one({"id": item_id}, {"$set": data})
        await audit(user, "editar", collection, item_id, "; ".join(mudancas) or "sem alterações", request)
        return _out({**atual, **data}, await ids_em_uso(acop_field))

    @router.patch("/{item_id}/status", response_model=out_model)
    async def alterar_status(item_id: str, body: StatusUpdate, request: Request, user: dict = Depends(require("write"))):
        atual = await _get(item_id)
        em_uso = await ids_em_uso(acop_field)
        if not body.ativo and item_id in em_uso:
            raise HTTPException(status_code=409, detail="Item está acoplado. Libere o acoplamento antes de inativar.")
        await coll.update_one({"id": item_id}, {"$set": {"ativo": body.ativo}})
        acao = "reativar" if body.ativo else "inativar"
        await audit(user, acao, collection, item_id, f"{unique_label}: {atual[unique_field]}", request)
        return _out({**atual, "ativo": body.ativo}, em_uso)

    return router
