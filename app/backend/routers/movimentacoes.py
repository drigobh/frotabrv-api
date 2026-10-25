from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.movimentacoes import MovimentacaoCreate, Movimentacao, InventarioPayload
import uuid

router = APIRouter(prefix="/estoque", tags=["movimentacoes"])

@router.get("/movimentacoes", response_model=list[Movimentacao])
async def listar_movimentacoes(_u: dict = Depends(require("read"))):
    docs = await db.movimentacoes.find({}, {"_id": 0}).sort("data_hora", -1).to_list(2000)
    return docs

@router.post("/movimentacoes", response_model=Movimentacao, status_code=201)
async def criar_movimentacao(body: MovimentacaoCreate, user: dict = Depends(require("write"))):
    peca = await db.pecas.find_one({"id": body.peca_id}, {"_id": 0})
    if not peca:
        raise HTTPException(404, "Peça não encontrada")

    if body.tipo == "saida" and peca["quantidade_estoque"] < body.quantidade:
        raise HTTPException(400, "Quantidade insuficiente em estoque para esta saída.")

    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["peca_nome"] = peca["nome"]
    doc["usuario_nome"] = user.get("nome", user.get("email", "Sistema"))
    doc["data_hora"] = now_iso()

    # Atualiza a quantidade na peça
    delta = body.quantidade if body.tipo == "entrada" else -body.quantidade
    await db.pecas.update_one({"id": body.peca_id}, {"$inc": {"quantidade_estoque": delta}})

    await db.movimentacoes.insert_one(doc)
    return doc

@router.post("/inventario")
async def realizar_inventario(body: InventarioPayload, user: dict = Depends(require("write"))):
    ajustes = 0
    for item in body.itens:
        peca = await db.pecas.find_one({"id": item.peca_id}, {"_id": 0})
        if peca:
            diff = item.quantidade_fisica - peca["quantidade_estoque"]
            if diff != 0:
                await db.pecas.update_one({"id": item.peca_id}, {"$set": {"quantidade_estoque": item.quantidade_fisica}})
                
                # Registrar movimentação de ajuste
                doc = {
                    "id": str(uuid.uuid4()),
                    "peca_id": item.peca_id,
                    "peca_nome": peca["nome"],
                    "tipo": "ajuste",
                    "quantidade": abs(diff),
                    "motivo": "Inventário Cíclico",
                    "observacao": f"Ajuste de {peca['quantidade_estoque']} para {item.quantidade_fisica}",
                    "usuario_nome": user.get("nome", user.get("email", "Sistema")),
                    "data_hora": now_iso()
                }
                await db.movimentacoes.insert_one(doc)
                ajustes += 1
    return {"ok": True, "ajustes": ajustes}
