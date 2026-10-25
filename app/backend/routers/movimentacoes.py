from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.movimentacoes import MovimentacaoCreate, Movimentacao, InventarioPayload, Inventario
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

    if peca["quantidade_estoque"] < body.quantidade:
        raise HTTPException(400, "Quantidade insuficiente em estoque.")

    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["peca_nome"] = peca["nome"]
    doc["usuario_nome"] = user.get("nome", user.get("email", "Sistema"))
    doc["data_hora"] = now_iso()

    if body.fornecedor_id:
        forn = await db.fornecedores.find_one({"id": body.fornecedor_id}, {"_id": 0})
        doc["fornecedor_nome"] = forn["nome"] if forn else None

    if body.veiculo_id:
        veic = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
        doc["destino_nome"] = f"Veículo: {veic['placa']}" if veic else None
    elif body.carreta_id:
        carr = await db.carretas.find_one({"id": body.carreta_id}, {"_id": 0})
        doc["destino_nome"] = f"Carreta: {carr['placa']}" if carr else None

    # Deduz do estoque
    await db.pecas.update_one({"id": body.peca_id}, {"$inc": {"quantidade_estoque": -body.quantidade}})

    await db.movimentacoes.insert_one(doc)
    return doc

@router.get("/inventarios", response_model=list[Inventario])
async def listar_inventarios(_u: dict = Depends(require("read"))):
    docs = await db.inventarios.find({}, {"_id": 0}).sort("data_hora", -1).to_list(2000)
    return docs

@router.post("/inventario")
async def realizar_inventario(body: InventarioPayload, user: dict = Depends(require("write"))):
    ajustes_reais = []
    
    for item in body.itens:
        if item.qtd_anterior != item.qtd_fisica:
            await db.pecas.update_one({"id": item.peca_id}, {"$set": {"quantidade_estoque": item.qtd_fisica}})
            ajustes_reais.append(item)
            
            # Registrar movimentação de ajuste
            doc_mov = {
                "id": str(uuid.uuid4()),
                "peca_id": item.peca_id,
                "peca_nome": item.peca_nome,
                "quantidade": abs(item.qtd_fisica - item.qtd_anterior),
                "motivo": "Inventário Cíclico",
                "observacao": f"Ajuste: {item.qtd_anterior} -> {item.qtd_fisica}",
                "usuario_nome": user.get("nome", "Sistema"),
                "data_hora": now_iso()
            }
            await db.movimentacoes.insert_one(doc_mov)

    if len(ajustes_reais) > 0:
        doc_inv = {
            "id": str(uuid.uuid4()),
            "data_hora": now_iso(),
            "usuario_nome": user.get("nome", user.get("email", "Sistema")),
            "total_ajustes": len(ajustes_reais),
            "itens": [i.model_dump() for i in ajustes_reais]
        }
        await db.inventarios.insert_one(doc_inv)

    return {"ok": True, "ajustes": len(ajustes_reais)}

@router.delete("/inventarios/{id}")
async def excluir_inventario(id: str, _u: dict = Depends(require("delete"))):
    await db.inventarios.delete_one({"id": id})
    return {"ok": True}
