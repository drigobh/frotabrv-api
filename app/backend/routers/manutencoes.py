from fastapi import APIRouter, Depends, HTTPException, Request
from lib.dates import now_iso
from lib.db import db
from lib.security import require
from models.manutencoes import Manutencao, ManutencaoCreate
import uuid

router = APIRouter(prefix="/manutencoes", tags=["manutencoes"])

@router.get("", response_model=None)
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.manutencoes.find({}, {"_id": 0}).sort("data", -1).to_list(2000)
    return docs

@router.post("", response_model=Manutencao, status_code=201)
async def criar(body: ManutencaoCreate, request: Request, user: dict = Depends(require("write"))):
    veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")

    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["veiculo_label"] = f"{veiculo['placa']} · {veiculo['modelo']}"
    doc["created_by"] = user["id"]
    doc["created_at"] = now_iso()

    await db.manutencoes.insert_one(doc)
    doc.pop("_id", None)
    return doc

@router.put("/{id}", response_model=Manutencao)
async def atualizar(id: str, body: ManutencaoCreate, request: Request, user: dict = Depends(require("write"))):
    existe = await db.manutencoes.find_one({"id": id})
    if not existe:
        raise HTTPException(404, "Manutenção não encontrada")

    veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")

    doc = body.model_dump()
    doc["veiculo_label"] = f"{veiculo['placa']} · {veiculo['modelo']}"
    
    await db.manutencoes.update_one({"id": id}, {"$set": doc})
    
    doc["id"] = id
    doc["created_at"] = existe.get("created_at", now_iso())
    doc["created_by"] = existe.get("created_by", user["id"])
    return doc

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    await db.manutencoes.delete_one({"id": id})
    return {"ok": True}
