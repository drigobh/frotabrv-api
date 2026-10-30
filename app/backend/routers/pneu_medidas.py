import uuid
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.pneu_medidas import PneuMedidaCreate, PneuMedida

router = APIRouter(prefix="/pneu-medidas", tags=["Pneu Medidas"])

@router.get("", response_model=list[PneuMedida])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.pneu_medidas.find({}, {"_id": 0}).sort("codigo", 1).to_list(500)
    return [PneuMedida(**d) for d in docs]

@router.post("", response_model=PneuMedida, status_code=201)
async def criar(body: PneuMedidaCreate, user: dict = Depends(require("write"))):
    existente = await db.pneu_medidas.find_one({"codigo": body.codigo})
    if existente:
        raise HTTPException(409, "Esta medida já está cadastrada.")
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    await db.pneu_medidas.insert_one(dict(doc))
    return PneuMedida(**doc)

@router.put("/{id}", response_model=PneuMedida)
async def atualizar(id: str, body: PneuMedidaCreate, user: dict = Depends(require("write"))):
    await db.pneu_medidas.update_one({"id": id}, {"$set": body.model_dump()})
    doc = await db.pneu_medidas.find_one({"id": id}, {"_id": 0})
    return PneuMedida(**doc)

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    await db.pneu_medidas.delete_one({"id": id})
    return {"ok": True}

@router.post("/seed")
async def seed_medidas(_u: dict = Depends(require("write"))):
    medidas = [
        {"codigo": "295/80 R22.5", "aro": "22.5", "tipo_construcao": "RADIAL", "requer_camara": False},
        {"codigo": "275/80 R22.5", "aro": "22.5", "tipo_construcao": "RADIAL", "requer_camara": False},
        {"codigo": "315/80 R22.5", "aro": "22.5", "tipo_construcao": "RADIAL", "requer_camara": False},
        {"codigo": "385/65 R22.5", "aro": "22.5", "tipo_construcao": "RADIAL", "requer_camara": False},
        {"codigo": "12 R22.5", "aro": "22.5", "tipo_construcao": "RADIAL", "requer_camara": False},
        {"codigo": "11.00 R22", "aro": "22.0", "tipo_construcao": "RADIAL", "requer_camara": True},
        {"codigo": "215/75 R17.5", "aro": "17.5", "tipo_construcao": "RADIAL", "requer_camara": False},
        {"codigo": "235/75 R17.5", "aro": "17.5", "tipo_construcao": "RADIAL", "requer_camara": False},
    ]
    inseridos = 0
    for m in medidas:
        existente = await db.pneu_medidas.find_one({"codigo": m["codigo"]})
        if not existente:
            m["id"] = str(uuid.uuid4())
            m["created_at"] = now_iso()
            await db.pneu_medidas.insert_one(dict(m))
            inseridos += 1
    return {"ok": True, "inseridos": inseridos}
