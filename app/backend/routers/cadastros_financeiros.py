from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from datetime import datetime
import uuid

router = APIRouter()

# --- BANCOS ---
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
        "saldo_inicial": float(body.get("saldo_inicial", 0))
    }
    await db.bancos.insert_one(novo)
    novo.pop("_id", None)
    return novo

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
        "tipo": body.get("tipo", "Ambos")
    }
    await db.categorias_financeiras.insert_one(novo)
    novo.pop("_id", None)
    return novo
