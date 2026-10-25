from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.pecas import Peca, PecaCreate
import uuid

router = APIRouter(prefix="/pecas", tags=["pecas"])

@router.get("", response_model=list[Peca])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.pecas.find({}, {"_id": 0}).sort("nome", 1).to_list(2000)
    return docs

@router.post("", response_model=Peca, status_code=201)
async def criar(body: PecaCreate, _u: dict = Depends(require("write"))):
    if body.codigo and await db.pecas.find_one({"codigo": body.codigo}):
        raise HTTPException(409, "Já existe uma peça com este código")
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    await db.pecas.insert_one(doc)
    return doc

@router.put("/{id}", response_model=Peca)
async def atualizar(id: str, body: PecaCreate, _u: dict = Depends(require("write"))):
    existe = await db.pecas.find_one({"id": id})
    if not existe:
        raise HTTPException(404, "Peça não encontrada")
    if body.codigo and await db.pecas.find_one({"codigo": body.codigo, "id": {"$ne": id}}):
        raise HTTPException(409, "Já existe outra peça com este código")
    
    doc = body.model_dump()
    await db.pecas.update_one({"id": id}, {"$set": doc})
    doc["id"] = id
    return doc

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    await db.pecas.delete_one({"id": id})
    return {"ok": True}
