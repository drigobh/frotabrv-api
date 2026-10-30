import uuid
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.pneu_marcas import PneuMarcaCreate, PneuMarca

router = APIRouter(prefix="/pneu-marcas", tags=["Pneu Marcas"])

@router.get("", response_model=list[PneuMarca])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.pneu_marcas.find({}, {"_id": 0}).sort("nome", 1).to_list(200)
    return [PneuMarca(**d) for d in docs]

@router.post("", response_model=PneuMarca, status_code=201)
async def criar(body: PneuMarcaCreate, user: dict = Depends(require("write"))):
    existente = await db.pneu_marcas.find_one({"nome": {"$regex": f"^{body.nome}$", "$options": "i"}})
    if existente:
        raise HTTPException(409, "Esta marca já está cadastrada.")
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    await db.pneu_marcas.insert_one(dict(doc))
    return PneuMarca(**doc)

@router.put("/{id}", response_model=PneuMarca)
async def atualizar(id: str, body: PneuMarcaCreate, user: dict = Depends(require("write"))):
    await db.pneu_marcas.update_one({"id": id}, {"$set": body.model_dump()})
    doc = await db.pneu_marcas.find_one({"id": id}, {"_id": 0})
    return PneuMarca(**doc)

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    await db.pneu_marcas.delete_one({"id": id})
    return {"ok": True}

@router.post("/seed")
async def seed_marcas(_u: dict = Depends(require("write"))):
    marcas = [
        {"nome": "Michelin", "tipo": "FABRICANTE_NOVO", "tier": "TIER_1"},
        {"nome": "Bridgestone", "tipo": "AMBOS", "tier": "TIER_1"},
        {"nome": "Goodyear", "tipo": "FABRICANTE_NOVO", "tier": "TIER_1"},
        {"nome": "Continental", "tipo": "FABRICANTE_NOVO", "tier": "TIER_1"},
        {"nome": "Prometeon (Pirelli)", "tipo": "FABRICANTE_NOVO", "tier": "TIER_1"},
        {"nome": "Dunlop", "tipo": "FABRICANTE_NOVO", "tier": "TIER_2"},
        {"nome": "Firestone", "tipo": "FABRICANTE_NOVO", "tier": "TIER_2"},
        {"nome": "Sailun", "tipo": "FABRICANTE_NOVO", "tier": "TIER_3"},
        {"nome": "Linglong", "tipo": "FABRICANTE_NOVO", "tier": "TIER_3"},
        {"nome": "Vipal", "tipo": "SISTEMA_REFORMA", "tier": None},
        {"nome": "Bandag", "tipo": "SISTEMA_REFORMA", "tier": None},
        {"nome": "Tipler", "tipo": "SISTEMA_REFORMA", "tier": None},
    ]
    inseridos = 0
    for m in marcas:
        existente = await db.pneu_marcas.find_one({"nome": {"$regex": f"^{m['nome']}$", "$options": "i"}})
        if not existente:
            m["id"] = str(uuid.uuid4())
            m["created_at"] = now_iso()
            await db.pneu_marcas.insert_one(dict(m))
            inseridos += 1
    return {"ok": True, "inseridos": inseridos}
