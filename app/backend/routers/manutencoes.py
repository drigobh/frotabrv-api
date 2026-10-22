import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from lib.audit import audit
from lib.dates import now_iso
from lib.db import db
from lib.security import require
from models.manutencoes import Manutencao, ManutencaoCreate

router = APIRouter(prefix="/manutencoes", tags=["manutencoes"])

@router.get("", response_model=list[Manutencao])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.manutencoes.find({}, {"_id": 0}).sort("data", -1).to_list(1000)
    return [Manutencao(**d) for d in docs]

@router.post("", response_model=Manutencao, status_code=201)
async def criar(body: ManutencaoCreate, request: Request, user: dict = Depends(require("write"))):
    veiculo = await db.veiculos.find_one({"id": body.veiculo_id})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")

    doc = {
        "id": str(uuid.uuid4()),
        **body.model_dump(),
        "veiculo_label": f"{veiculo['placa']} - {veiculo.get('modelo', '')}",
        "created_by": user["nome"],
        "created_at": now_iso()
    }
    
    await db.manutencoes.insert_one(dict(doc))
    await audit(user, "criar", "manutencoes", doc["id"], f"Veículo: {doc['veiculo_label']}", request)
    return Manutencao(**doc)
