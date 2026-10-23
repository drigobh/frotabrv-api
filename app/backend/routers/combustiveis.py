from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.combustiveis import Combustivel, CombustivelCreate
import uuid

router = APIRouter(prefix="/combustiveis", tags=["combustiveis"])

@router.get("", response_model=list[Combustivel])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.combustiveis.find({}, {"_id": 0}).sort("nome", 1).to_list(1000)
    return docs

@router.post("", response_model=Combustivel, status_code=201)
async def criar(body: CombustivelCreate, _u: dict = Depends(require("write"))):
    if await db.combustiveis.find_one({"nome": body.nome}):
        raise HTTPException(409, "Combustível já cadastrado")
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    await db.combustiveis.insert_one(doc)
    return doc

@router.put("/{id}", response_model=Combustivel)
async def atualizar(id: str, body: CombustivelCreate, _u: dict = Depends(require("write"))):
    existe = await db.combustiveis.find_one({"id": id})
    if not existe:
        raise HTTPException(404, "Combustível não encontrado")
    
    # Verifica se o novo nome já existe em outro registro
    if await db.combustiveis.find_one({"nome": body.nome, "id": {"$ne": id}}):
        raise HTTPException(409, "Já existe outro combustível com este nome")
    
    doc = body.model_dump()
    await db.combustiveis.update_one({"id": id}, {"$set": doc})
    doc["id"] = id
    return doc

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    # Verifica se está em uso em algum abastecimento
    em_uso = await db.abastecimentos.find_one({"combustivel_id": id})
    if em_uso:
        raise HTTPException(400, "Não é possível excluir: combustível em uso em abastecimentos.")
    
    await db.combustiveis.delete_one({"id": id})
    return {"ok": True}
