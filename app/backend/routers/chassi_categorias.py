from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from pymongo.errors import DuplicateKeyError

from lib.chassi_vinculos import transacao_chassi
from lib.db import db
from lib.security import require


router = APIRouter(prefix="/chassi-categorias", tags=["Categorias de Chassi"])


class NomeCategoria(BaseModel):
    nome: str = Field(min_length=1, max_length=100)


class NovaCategoria(NomeCategoria):
    familia: str = Field(min_length=1, max_length=80)


class EdicaoCategoria(NomeCategoria):
    familia: str | None = Field(default=None, min_length=1, max_length=80)


class StatusCategoria(BaseModel):
    ativo: bool


def nome_categoria(body):
    nome = " ".join(body.nome.split())
    if not nome:
        raise HTTPException(422, "Informe o nome da categoria.")
    return {"nome": nome, "nome_chave": nome.casefold()}


async def exigir_tipo_ativo(codigo, session):
    if not await db.chassi_tipos_aplicacao.find_one({"_id": codigo, "ativo": True}, session=session):
        raise HTTPException(409, "Selecione um tipo de aplicação ativo.")


def resposta(doc):
    return {"id": doc["_id"], "nome": doc["nome"], "familia": doc["familia"], "ativo": doc["ativo"]}


@router.get("")
async def listar(_u: dict = Depends(require("read"))):
    cursor = db.chassi_categorias.find().sort("nome", 1)
    return [resposta(doc) async for doc in cursor]


@router.post("", status_code=201)
async def criar(body: NovaCategoria, _u: dict = Depends(require("write"))):
    doc = {"_id": str(uuid4()), **nome_categoria(body), "familia": body.familia, "ativo": True}
    async def inserir(session):
        await exigir_tipo_ativo(body.familia, session)
        await db.chassi_categorias.insert_one(dict(doc), session=session)

    try:
        await transacao_chassi(inserir)
    except DuplicateKeyError:
        raise HTTPException(409, "Já existe uma categoria com esse nome.") from None
    return resposta(doc)


@router.put("/{codigo}")
async def editar(codigo: str, body: EdicaoCategoria, _u: dict = Depends(require("write"))):
    async def alterar(session):
        atual = await db.chassi_categorias.find_one({"_id": codigo}, session=session)
        if not atual:
            raise HTTPException(404, "Categoria não encontrada.")
        campos = nome_categoria(body)
        if body.familia is not None and body.familia != atual["familia"]:
            if await db.chassi_templates.find_one({"categoria": codigo}, {"_id": 1}, session=session):
                raise HTTPException(409, "Esta categoria já está em uso. O tipo de aplicação não pode ser alterado.")
            await exigir_tipo_ativo(body.familia, session)
            campos["familia"] = body.familia
        await db.chassi_categorias.update_one({"_id": codigo}, {"$set": campos}, session=session)

    try:
        await transacao_chassi(alterar)
    except DuplicateKeyError:
        raise HTTPException(409, "Já existe uma categoria com esse nome.") from None
    return {"ok": True}


@router.patch("/{codigo}/status")
async def alterar_status(codigo: str, body: StatusCategoria, _u: dict = Depends(require("write"))):
    async def alterar(session):
        resultado = await db.chassi_categorias.update_one(
            {"_id": codigo}, {"$set": {"ativo": body.ativo}}, session=session
        )
        if not resultado.matched_count:
            raise HTTPException(404, "Categoria não encontrada.")
    await transacao_chassi(alterar)
    return {"ok": True}


@router.delete("/{codigo}")
async def excluir(codigo: str, _u: dict = Depends(require("delete"))):
    async def remover(session):
        if await db.chassi_templates.find_one({"categoria": codigo}, {"_id": 1}, session=session):
            raise HTTPException(409, "Categoria usada por um template de chassi. Altere o vínculo antes de excluir.")
        resultado = await db.chassi_categorias.delete_one({"_id": codigo}, session=session)
        if not resultado.deleted_count:
            raise HTTPException(404, "Categoria não encontrada.")
    await transacao_chassi(remover)
    return {"ok": True}
