from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from datetime import datetime
import uuid

router = APIRouter()

@router.get("")
async def listar_multas(_u: dict = Depends(require("read"))):
    return await db.multas.find({}, {"_id": 0}).sort("data_infracao", -1).to_list(1000)

@router.post("")
async def criar_multa(body: dict, _u: dict = Depends(require("write"))):
    novo = {
        "id": str(uuid.uuid4()),
        "veiculo_id": body.get("veiculo_id"),
        "motorista_id": body.get("motorista_id"),
        "data_infracao": body.get("data_infracao"),
        "hora_infracao": body.get("hora_infracao", ""),
        "local": body.get("local", ""),
        "descricao": body.get("descricao", ""),
        "valor": float(body.get("valor", 0)),
        "pontos": int(body.get("pontos", 0)),
        "orgao_autuador": body.get("orgao_autuador", ""),
        "numero_ait": body.get("numero_ait", ""),
        "status": body.get("status", "Pendente"),
        "created_at": datetime.now().isoformat()
    }
    await db.multas.insert_one(novo)
    novo.pop("_id", None)
    return novo

@router.put("/{id}")
async def atualizar_multa(id: str, body: dict, _u: dict = Depends(require("write"))):
    update = {k: v for k, v in body.items() if k in [
        "veiculo_id", "motorista_id", "data_infracao", "hora_infracao", "local", 
        "descricao", "valor", "pontos", "orgao_autuador", "numero_ait", "status"
    ]}
    await db.multas.update_one({"id": id}, {"$set": update})
    return {"status": "ok"}

@router.delete("/{id}")
async def excluir_multa(id: str, _u: dict = Depends(require("write"))):
    await db.multas.delete_one({"id": id})
    return {"status": "ok"}
