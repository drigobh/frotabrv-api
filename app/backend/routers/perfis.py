from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
import uuid

router = APIRouter()

@router.get("")
async def listar_perfis(_u: dict = Depends(require("read"))):
    return await db.perfis.find({}, {"_id": 0}).to_list(100)

@router.post("")
async def criar_perfil(body: dict, _u: dict = Depends(require("write"))):
    novo = {
        "id": str(uuid.uuid4()),
        "nome": body.get("nome"),
        "descricao": body.get("descricao", ""),
        "permissoes": body.get("permissoes", []),
    }
    await db.perfis.insert_one(novo)
    novo.pop("_id", None)
    return novo

@router.put("/{id}")
async def atualizar_perfil(id: str, body: dict, _u: dict = Depends(require("write"))):
    await db.perfis.update_one({"id": id}, {"$set": body})
    return {"status": "ok"}

@router.delete("/{id}")
async def excluir_perfil(id: str, _u: dict = Depends(require("write"))):
    await db.perfis.delete_one({"id": id})
    return {"status": "ok"}
