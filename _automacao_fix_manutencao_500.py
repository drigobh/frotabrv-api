import os

def fix_models(raiz):
    caminho = os.path.join(raiz, "app", "backend", "models", "manutencoes.py")
    codigo = '''from pydantic import BaseModel, Field
from typing import Optional

class ManutencaoCreate(BaseModel):
    veiculo_id: str
    tipo: str
    status: str
    descricao: str
    data: str = Field(pattern=r"^\\d{4}-\\d{2}-\\d{2}$")
    custo: float = 0.0
    oficina: Optional[str] = None
    km_manutencao: Optional[float] = None
    proxima_revisao_km: Optional[float] = None
    pecas_substituidas: Optional[str] = None

class Manutencao(ManutencaoCreate):
    id: str
    veiculo_label: str
    created_at: str
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Modelo de Manutenção atualizado com todos os campos do formulário.")

def fix_router(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "manutencoes.py")
    codigo = '''from fastapi import APIRouter, Depends, HTTPException, Request
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
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Router de Manutenções reescrito com as rotas PUT e DELETE.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_models(raiz)
    fix_router(raiz)