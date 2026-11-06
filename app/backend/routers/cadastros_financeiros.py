from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from datetime import datetime
import uuid

router = APIRouter()

# ==========================================
# BANCOS
# ==========================================
@router.get("/bancos")
async def listar_bancos(_u: dict = Depends(require("read"))):
    return await db.bancos.find({}, {"_id": 0}).to_list(100)

@router.post("/bancos")
async def criar_banco(body: dict, _u: dict = Depends(require("write"))):
    novo = {
        "id": str(uuid.uuid4()),
        "nome": body.get("nome"),
        "agencia": body.get("agencia", ""),
        "numero_agencia": body.get("numero_agencia", ""),
        "conta": body.get("conta", ""),
        "telefone": body.get("telefone", ""),
        "contato": body.get("contato", ""),
        "whatsapp": body.get("whatsapp", ""),
        "ativo": True,
        "saldo_inicial": float(body.get("saldo_inicial", 0))
    }
    await db.bancos.insert_one(novo)
    novo.pop("_id", None)
    return novo

@router.put("/bancos/{id}")
async def atualizar_banco(id: str, body: dict, _u: dict = Depends(require("write"))):
    update = {k: v for k, v in body.items() if k in [
        "nome", "agencia", "numero_agencia", "conta", "telefone", "contato", "whatsapp", "saldo_inicial"
    ]}
    await db.bancos.update_one({"id": id}, {"$set": update})
    return {"status": "ok"}

@router.patch("/bancos/{id}/status")
async def alternar_status_banco(id: str, body: dict, _u: dict = Depends(require("write"))):
    ativo = body.get("ativo", True)
    await db.bancos.update_one({"id": id}, {"$set": {"ativo": ativo}})
    return {"status": "ok", "ativo": ativo}

@router.delete("/bancos/{id}")
async def excluir_banco(id: str, _u: dict = Depends(require("write"))):
    await db.bancos.delete_one({"id": id})
    return {"status": "ok"}

# ==========================================
# CATEGORIAS FINANCEIRAS
# ==========================================
@router.get("/categorias")
async def listar_categorias(tipo: str = None, _u: dict = Depends(require("read"))):
    filtro = {}
    if tipo:
        filtro["tipo"] = tipo
    return await db.categorias_financeiras.find(filtro, {"_id": 0}).to_list(100)

@router.post("/categorias")
async def criar_categoria(body: dict, _u: dict = Depends(require("write"))):
    novo = {
        "id": str(uuid.uuid4()),
        "nome": body.get("nome"),
        "tipo": body.get("tipo", "Ambos"),
        "ativo": True
    }
    await db.categorias_financeiras.insert_one(novo)
    novo.pop("_id", None)
    return novo

@router.put("/categorias/{id}")
async def atualizar_categoria(id: str, body: dict, _u: dict = Depends(require("write"))):
    update = {k: v for k, v in body.items() if k in ["nome", "tipo"]}
    await db.categorias_financeiras.update_one({"id": id}, {"$set": update})
    return {"status": "ok"}

@router.patch("/categorias/{id}/status")
async def alternar_status_categoria(id: str, body: dict, _u: dict = Depends(require("write"))):
    ativo = body.get("ativo", True)
    await db.categorias_financeiras.update_one({"id": id}, {"$set": {"ativo": ativo}})
    return {"status": "ok", "ativo": ativo}

@router.delete("/categorias/{id}")
async def excluir_categoria(id: str, _u: dict = Depends(require("write"))):
    await db.categorias_financeiras.delete_one({"id": id})
    return {"status": "ok"}
