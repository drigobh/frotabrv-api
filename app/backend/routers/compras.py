from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import uuid
from models.compras import PedidoCompraCreate, AprovacaoPayload
from lib.db import db
from .auth import require

router = APIRouter(prefix="/compras", tags=["Compras"])

async def gerar_numero_pedido():
    res = await db.contadores.find_one_and_update(
        {"_id": "compras"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    seq = res.get("seq", 1) if res else 1
    return f"OC-{seq:04d}"

@router.post("")
async def criar_pedido(payload: PedidoCompraCreate, _u: dict = Depends(require("write"))):
    try:
        doc = {
            "id": str(uuid.uuid4()),
            "numero": await gerar_numero_pedido(),
            "fornecedor_id": payload.fornecedor_id,
            "veiculo_id": payload.veiculo_id,
            "itens": [item.model_dump() for item in payload.itens],
            "observacoes": payload.observacoes,
            "valor_total": payload.valor_total,
            "status": "Pendente",  # Pendente, Aprovado, Reprovado, Comprado
            "data_criacao": datetime.now().isoformat(),
            "criado_por": _u.get("nome", "Sistema")
        }
        await db.compras.insert_one(doc)
        doc.pop("_id", None)
        return doc
    except Exception as e:
        raise HTTPException(400, f"Erro ao criar pedido: {str(e)}")

@router.get("")
async def listar_pedidos(status: str = None, _u: dict = Depends(require("read"))):
    filtro = {}
    if status:
        filtro["status"] = status
    return await db.compras.find(filtro, {"_id": 0}).sort("data_criacao", -1).to_list(1000)

@router.patch("/{id}/aprovar")
async def aprovar_pedido(id: str, payload: AprovacaoPayload, _u: dict = Depends(require("write"))):
    pedido = await db.compras.find_one({"id": id})
    if not pedido:
        raise HTTPException(404, "Pedido não encontrado")
    
    if payload.status not in ["Aprovado", "Reprovado"]:
        raise HTTPException(400, "Status inválido")

    await db.compras.update_one(
        {"id": id},
        {"$set": {
            "status": payload.status,
            "aprovado_por": _u.get("nome", "Sistema"),
            "data_aprovacao": datetime.now().isoformat(),
            "motivo_reprovacao": payload.motivo
        }}
    )
    return {"ok": True}

@router.delete("/{id}")
async def excluir_pedido(id: str, _u: dict = Depends(require("write"))):
    await db.compras.delete_one({"id": id})
    return {"ok": True}
