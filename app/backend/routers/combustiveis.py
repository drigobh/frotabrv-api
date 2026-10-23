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
