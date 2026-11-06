from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from datetime import datetime
import uuid

router = APIRouter()

@router.get("/contas")
async def listar_contas(tipo: str = None, mes: str = None, ano: str = None, _u: dict = Depends(require("read"))):
    filtro = {}
    if tipo:
        filtro["tipo"] = tipo
    if ano and ano != "0":
        if mes and mes != "0":
            # Mês específico
            prefixo = f"{ano}-{str(mes).zfill(2)}"
            filtro["vencimento"] = {"$regex": f"^{prefixo}"}
        else:
            # Todos os meses do ano
            filtro["vencimento"] = {"$regex": f"^{ano}"}
    
    return await db.contas.find(filtro, {"_id": 0}).sort("vencimento", 1).to_list(1000)

@router.post("/contas")
async def criar_conta(body: dict, _u: dict = Depends(require("write"))):
    novo = {
        "id": str(uuid.uuid4()),
        "tipo": body.get("tipo", "Pagar"),
        "descricao": body.get("descricao", ""),
        "categoria": body.get("categoria", "Outros"),
        "valor": float(body.get("valor", 0)),
        "vencimento": body.get("vencimento"),
        "status": body.get("status", "Pendente"),
        "fornecedor_id": body.get("fornecedor_id"),
        "veiculo_id": body.get("veiculo_id"),
        "documento_vinculo": body.get("documento_vinculo", ""),
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
async def resumo_financeiro(mes: str = None, ano: str = None, _u: dict = Depends(require("read"))):
    filtro = {}
    if ano and ano != "0":
        if mes and mes != "0":
            prefixo = f"{ano}-{str(mes).zfill(2)}"
            filtro["vencimento"] = {"$regex": f"^{prefixo}"}
        else:
            filtro["vencimento"] = {"$regex": f"^{ano}"}

    contas = await db.contas.find(filtro, {"_id": 0}).to_list(1000)
    
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

@router.get("/conciliacao")
async def conciliacao(mes: str = None, ano: str = None, _u: dict = Depends(require("read"))):
    filtro = {}
    if ano and ano != "0":
        if mes and mes != "0":
            prefixo = f"{ano}-{str(mes).zfill(2)}"
            filtro["vencimento"] = {"$regex": f"^{prefixo}"}
        else:
            filtro["vencimento"] = {"$regex": f"^{ano}"}

    contas = await db.contas.find(filtro, {"_id": 0}).to_list(1000)
    
    total_pagar = sum(c["valor"] for c in contas if c.get("tipo") == "Pagar")
    total_receber = sum(c["valor"] for c in contas if c.get("tipo") == "Receber")
    pago = sum(c["valor"] for c in contas if c.get("status") == "Pago")
    pendente = sum(c["valor"] for c in contas if c.get("status") == "Pendente")
    atrasado = sum(c["valor"] for c in contas if c.get("status") == "Atrasado")

    return {
        "total_pagar": total_pagar,
        "total_receber": total_receber,
        "pago": pago,
        "pendente": pendente,
        "atrasado": atrasado,
        "saldo": total_receber - total_pagar,
        "contas": contas
    }

