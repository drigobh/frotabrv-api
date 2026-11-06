from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
import datetime
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

@router.post("/contas", response_model=dict)
async def criar_conta(payload: dict, _u: dict = Depends(require("write"))):
    try:
        doc = {
            "id": str(__import__("uuid").uuid4()),
            "tipo": payload.get("tipo", "Pagar"),
            "descricao": payload.get("descricao", ""),
            "categoria": payload.get("categoria", "Outros"),
            "valor": float(payload.get("valor", 0) or 0),
            "vencimento": payload.get("vencimento", ""),
            "status": payload.get("status", "Pendente"),
            "fornecedor_id": payload.get("fornecedor_id") or None,
            "veiculo_id": payload.get("veiculo_id") or None,
            "documento_vinculo": payload.get("documento_vinculo") or "",
            "observacoes": payload.get("observacoes", ""),
            "origem": payload.get("origem") or "Manual",
            "xml_original": payload.get("xml_original") or "",
            "criado_por": _u.get("nome", _u.get("email", "Sistema")),
            "criado_em": datetime.datetime.now().isoformat(),
            "historico": []
        }
        await db.contas.insert_one(doc)
        doc.pop("_id", None)
        return doc
    except Exception as e:
        raise HTTPException(400, f"Erro ao criar conta: {str(e)}")

@router.put("/contas/{id}")
async def atualizar_conta(id: str, body: dict, _u: dict = Depends(require("write"))):
    update = {k: v for k, v in body.items() if k in [
        "descricao", "categoria", "valor", "vencimento", "status", "vinculo", "observacoes"
    ]}
    await db.contas.update_one({"id": id}, {"$set": update})
    return {"status": "ok"}

@router.patch("/contas/{id}/pagar")
async def pagar_conta(id: str, _u: dict = Depends(require("write"))):
    conta = await db.contas.find_one({"id": id})
    if not conta:
        raise HTTPException(404, "Conta não encontrada")
    
    historico = conta.get("historico", [])
    historico.append({
        "acao": "Baixa",
        "data": datetime.datetime.now().isoformat(),
        "usuario": _u.get("nome", _u.get("email", "Sistema")),
        "valor": conta.get("valor")
    })
    
    await db.contas.update_one(
        {"id": id},
        {"$set": {
            "status": "Pago",
            "data_pagamento": datetime.datetime.now().isoformat(),
            "historico": historico
        }}
    )
    return {"ok": True}

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



@router.patch("/contas/{id}/estornar")
async def estornar_conta(id: str, _u: dict = Depends(require("write"))):
    conta = await db.contas.find_one({"id": id})
    if not conta: raise HTTPException(404, "Conta não encontrada")
    
    historico = conta.get("historico", [])
    historico.append({
        "acao": "Estorno",
        "data": datetime.datetime.now().isoformat(),
        "usuario": _u.get("nome", "Sistema"),
        "valor": conta.get("valor")
    })
    
    await db.contas.update_one(
        {"id": id}, 
        {"$set": {"status": "Pendente", "historico": historico}, "$unset": {"data_pagamento": ""}}
    )
    return {"ok": True}


@router.get("/contas/{id}/xml")
async def obter_xml_conta(id: str, _u: dict = Depends(require("read"))):
    conta = await db.contas.find_one({"id": id}, {"_id": 0, "xml_original": 1, "documento_vinculo": 1})
    if not conta:
        raise HTTPException(404, "Conta não encontrada")
    if not conta.get("xml_original"):
        raise HTTPException(404, "Esta conta não tem XML armazenado")
    return {"xml": conta["xml_original"], "chave": conta.get("documento_vinculo", "")}


@router.get("/xml/{chave}")
async def obter_xml_por_chave(chave: str, _u: dict = Depends(require("read"))):
    conta = await db.contas.find_one({"documento_vinculo": chave}, {"_id": 0, "xml_original": 1, "documento_vinculo": 1})
    if not conta:
        raise HTTPException(404, "XML não encontrado para esta chave")
    if not conta.get("xml_original"):
        raise HTTPException(404, "XML não foi salvo nesta conta")
    return {"xml": conta["xml_original"], "chave": conta["documento_vinculo"]}
