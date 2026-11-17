from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import DuplicateKeyError

from lib.chassi_vinculos import transacao_chassi
from lib.db import db
from lib.security import require
from routers.chassi_categorias import NomeCategoria, StatusCategoria, nome_categoria


router = APIRouter(prefix="/chassi-tipos-aplicacao", tags=["Tipos de Aplicação de Chassi"])


class TipoAplicacao(NomeCategoria):
    destino: Literal["CAVALO", "CARRETA", "SEM_VINCULO"]


def resposta(doc):
    return {"id": doc["_id"], "nome": doc["nome"], "destino": doc["destino"], "ativo": doc["ativo"]}


async def conferir_vinculo(codigo, session):
    if await db.chassi_categorias.find_one({"familia": codigo}, {"_id": 1}, session=session):
        raise HTTPException(409, "Tipo de aplicação usado por uma categoria de chassi.")


@router.get("")
async def listar(_u: dict = Depends(require("read"))):
    return [resposta(doc) async for doc in db.chassi_tipos_aplicacao.find().sort("nome", 1)]


@router.post("", status_code=201)
async def criar(body: TipoAplicacao, _u: dict = Depends(require("write"))):
    doc = {"_id": str(uuid4()), **nome_categoria(body), "destino": body.destino, "ativo": True}
    try:
        await db.chassi_tipos_aplicacao.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(409, "Já existe um tipo de aplicação com esse nome.") from None
    return resposta(doc)


@router.put("/{codigo}")
async def editar(codigo: str, body: TipoAplicacao, _u: dict = Depends(require("write"))):
    async def alterar(session):
        atual = await db.chassi_tipos_aplicacao.find_one({"_id": codigo}, session=session)
        if not atual:
            raise HTTPException(404, "Tipo de aplicação não encontrado.")
        if atual["destino"] != body.destino:
            await conferir_vinculo(codigo, session)
        campos = {**nome_categoria(body), "destino": body.destino}
        await db.chassi_tipos_aplicacao.update_one({"_id": codigo}, {"$set": campos}, session=session)
        return resposta({**atual, **campos})
    try:
        return await transacao_chassi(alterar)
    except DuplicateKeyError:
        raise HTTPException(409, "Já existe um tipo de aplicação com esse nome.") from None


@router.patch("/{codigo}/status")
async def alterar_status(codigo: str, body: StatusCategoria, _u: dict = Depends(require("write"))):
    async def alterar(session):
        resultado = await db.chassi_tipos_aplicacao.update_one(
            {"_id": codigo}, {"$set": {"ativo": body.ativo}}, session=session
        )
        if not resultado.matched_count:
            raise HTTPException(404, "Tipo de aplicação não encontrado.")
    await transacao_chassi(alterar)
    return {"ok": True}


@router.delete("/{codigo}")
async def excluir(codigo: str, _u: dict = Depends(require("delete"))):
    async def remover(session):
        await conferir_vinculo(codigo, session)
        resultado = await db.chassi_tipos_aplicacao.delete_one({"_id": codigo}, session=session)
        if not resultado.deleted_count:
            raise HTTPException(404, "Tipo de aplicação não encontrado.")
    await transacao_chassi(remover)
    return {"ok": True}
