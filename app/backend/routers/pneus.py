import uuid
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.pneus import PneuCreate, Pneu

router = APIRouter(prefix="/pneus", tags=["Pneus"])

@router.get("", response_model=list[Pneu])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.pneus.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return [Pneu(**d) for d in docs]

@router.post("", response_model=Pneu, status_code=201)
async def criar(body: PneuCreate, user: dict = Depends(require("write"))):
    # Verifica se o número de fogo já existe
    existente = await db.pneus.find_one({"numero_fogo": body.numero_fogo})
    if existente:
        raise HTTPException(409, "Este número de fogo já está cadastrado.")

    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    doc["created_by"] = user["nome"]
    
    await db.pneus.insert_one(dict(doc))
    return Pneu(**doc)

@router.put("/{id}", response_model=Pneu)
async def atualizar(id: str, body: PneuCreate, user: dict = Depends(require("write"))):
    existe = await db.pneus.find_one({"id": id})
    if not existe:
        raise HTTPException(404, "Pneu não encontrado.")
    
    doc = body.model_dump()
    doc["updated_at"] = now_iso()
    doc["updated_by"] = user["nome"]
    
    await db.pneus.update_one({"id": id}, {"$set": doc})
    doc = await db.pneus.find_one({"id": id}, {"_id": 0})
    return Pneu(**doc)

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    await db.pneus.delete_one({"id": id})
    return {"ok": True}
