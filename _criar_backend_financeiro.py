import os
import re

# 1. Criar o router financeiro
path_fin = os.path.join(os.getcwd(), "app", "backend", "routers", "financeiro.py")

conteudo = r'''from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from datetime import datetime
import uuid

router = APIRouter()

@router.get("/contas")
async def listar_contas(tipo: str = None, _u: dict = Depends(require("read"))):
    filtro = {}
    if tipo:
        filtro["tipo"] = tipo
    return await db.contas.find(filtro, {"_id": 0}).sort("vencimento", 1).to_list(1000)

@router.post("/contas")
async def criar_conta(body: dict, _u: dict = Depends(require("write"))):
    novo = {
        "id": str(uuid.uuid4()),
        "tipo": body.get("tipo", "Pagar"), # Pagar ou Receber
        "descricao": body.get("descricao", ""),
        "categoria": body.get("categoria", "Outros"),
        "valor": float(body.get("valor", 0)),
        "vencimento": body.get("vencimento"),
        "status": body.get("status", "Pendente"), # Pendente, Pago, Atrasado
        "vinculo": body.get("vinculo", ""),
        "observacoes": body.get("observacoes", ""),
        "created_at": datetime.now().isoformat()
    }
    await db.contas.insert_one(novo)
    novo.pop("_id", None)
    return novo

@router.put("/contas/{id}")
async def atualizar_conta(id: str, body: dict, _u: dict = Depends(require("write"))):
    update = {k: v for k, v in body.items() if k in [
        "descricao", "categoria", "valor", "vencimento", "status", "vinculo", "observacoes"
    ]}
    await db.contas.update_one({"id": id}, {"$set": update})
    return {"status": "ok"}

@router.patch("/contas/{id}/pagar")
async def marcar_pago(id: str, _u: dict = Depends(require("write"))):
    await db.contas.update_one({"id": id}, {"$set": {"status": "Pago", "data_pagamento": datetime.now().isoformat()}})
    return {"status": "ok"}

@router.delete("/contas/{id}")
async def excluir_conta(id: str, _u: dict = Depends(require("write"))):
    await db.contas.delete_one({"id": id})
    return {"status": "ok"}

@router.get("/resumo")
async def resumo_financeiro(_u: dict = Depends(require("read"))):
    contas = await db.contas.find({}, {"_id": 0}).to_list(1000)
    
    a_pagar = sum(c["valor"] for c in contas if c.get("tipo") == "Pagar" and c.get("status") == "Pendente")
    a_receber = sum(c["valor"] for c in contas if c.get("tipo") == "Receber" and c.get("status") == "Pendente")
    vencido = sum(c["valor"] for c in contas if c.get("status") == "Atrasado")
    total_pago = sum(c["valor"] for c in contas if c.get("status") == "Pago")
    
    return {
        "a_pagar": a_pagar,
        "a_receber": a_receber,
        "vencido": vencido,
        "total_pago": total_pago,
        "saldo": a_receber - a_pagar
    }
'''

with open(path_fin, "w", encoding="utf-8") as f:
    f.write(conteudo)
print("✅ Backend: Router financeiro criado.")

# 2. Registrar no server.py
path_server = os.path.join(os.getcwd(), "app", "backend", "server.py")
with open(path_server, "r", encoding="utf-8") as f:
    s_c = f.read()

if "financeiro" not in s_c:
    match_import = re.search(r'from routers import ([^\n]+)', s_c)
    if match_import:
        s_c = s_c.replace(match_import.group(1), match_import.group(1) + ", financeiro")
    
    match_include = re.search(r'api_router\.include_router\(multas\.router[^\n]*\n', s_c)
    if match_include:
        s_c = s_c.replace(match_include.group(0), match_include.group(0) + 'api_router.include_router(financeiro.router, prefix="/financeiro", tags=["financeiro"])\n')
    else:
        s_c += '\napi_router.include_router(financeiro.router, prefix="/financeiro", tags=["financeiro"])\n'
    
    with open(path_server, "w", encoding="utf-8") as f:
        f.write(s_c)
    print("✅ Server: Router financeiro registrado.")