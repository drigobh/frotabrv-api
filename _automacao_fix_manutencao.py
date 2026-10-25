import os

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "manutencoes.py")
    
    codigo = '''from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.manutencoes import ManutencaoCreate, Manutencao
import uuid

router = APIRouter(prefix="/manutencoes", tags=["manutencoes"])

@router.get("", response_model=None)
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.manutencoes.find({}, {"_id": 0}).sort("data", -1).to_list(2000)
    return docs

@router.post("", response_model=Manutencao, status_code=201)
async def criar(body: ManutencaoCreate, _u: dict = Depends(require("write"))):
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    
    veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    if veiculo:
        doc["veiculo_label"] = f"{veiculo['placa']} · {veiculo['modelo']}"
    else:
        raise HTTPException(404, "Veículo não encontrado")

    doc["created_at"] = now_iso()
    await db.manutencoes.insert_one(doc)
    doc.pop("_id", None)
    return doc

@router.put("/{id}", response_model=Manutencao)
async def atualizar(id: str, body: ManutencaoCreate, _u: dict = Depends(require("write"))):
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
    return doc

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    await db.manutencoes.delete_one({"id": id})
    return {"ok": True}
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Backend de Manutenções reescrito com as rotas PUT e DELETE.")

if __name__ == "__main__":
    fix_backend(os.getcwd())