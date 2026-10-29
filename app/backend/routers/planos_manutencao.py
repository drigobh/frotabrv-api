import uuid
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.planos_manutencao import PlanoManutencaoCreate, PlanoManutencao

router = APIRouter(prefix="/planos-manutencao", tags=["Planos de Manutenção"])

@router.get("", response_model=list[PlanoManutencao])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.planos_manutencao.find({}, {"_id": 0}).to_list(1000)
    return [PlanoManutencao(**d) for d in docs]

@router.post("", response_model=PlanoManutencao, status_code=201)
async def criar(body: PlanoManutencaoCreate, _u: dict = Depends(require("write"))):
    veiculo = None
    if body.veiculo_id:
        veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    elif body.carreta_id:
        veiculo = await db.carretas.find_one({"id": body.carreta_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")
    
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["veiculo_label"] = f"{veiculo.get('placa', veiculo.get('codigo', ''))} - {veiculo.get('modelo', '')}"
    doc["created_at"] = now_iso()
    doc["created_by"] = user["nome"]
    
    await db.planos_manutencao.insert_one(dict(doc))
    return PlanoManutencao(**doc)

@router.put("/{id}", response_model=PlanoManutencao)
async def atualizar(id: str, body: PlanoManutencaoCreate, _u: dict = Depends(require("write"))):
    veiculo = None
    if body.veiculo_id:
        veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    elif body.carreta_id:
        veiculo = await db.carretas.find_one({"id": body.carreta_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")
        
    doc = body.model_dump()
    doc["veiculo_label"] = f"{veiculo.get('placa', veiculo.get('codigo', ''))} - {veiculo.get('modelo', '')}"
    
    await db.planos_manutencao.update_one({"id": id}, {"$set": doc})
    doc = await db.planos_manutencao.find_one({"id": id}, {"_id": 0})
    return PlanoManutencao(**doc)

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    await db.planos_manutencao.delete_one({"id": id})
    return {"ok": True}
