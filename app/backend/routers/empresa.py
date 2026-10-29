import uuid
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.empresa import EmpresaBase, Empresa

router = APIRouter(prefix="/empresa", tags=["Empresa"])

@router.get("", response_model=Empresa)
async def obter(_u: dict = Depends(require("read"))):
    doc = await db.empresa.find_one({"id": "empresa_atual"}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Empresa não cadastrada")
    return Empresa(**doc)

@router.put("", response_model=Empresa)
async def atualizar(body: EmpresaBase, user: dict = Depends(require("write"))):
    doc = body.model_dump()
    doc["id"] = "empresa_atual"
    doc["updated_at"] = now_iso()
    
    existente = await db.empresa.find_one({"id": "empresa_atual"})
    if not existente:
        doc["created_at"] = doc["updated_at"]
    else:
        doc["created_at"] = existente.get("created_at", doc["updated_at"])

    await db.empresa.update_one(
        {"id": "empresa_atual"},
        {"$set": doc},
        upsert=True
    )
    return Empresa(**doc)
