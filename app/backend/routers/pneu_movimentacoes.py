import uuid
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.pneu_movimentacoes import PneuMovimentacaoCreate, PneuMovimentacao

router = APIRouter(prefix="/pneu-movimentacoes", tags=["Pneu Movimentações"])

@router.get("", response_model=list[PneuMovimentacao])
async def listar(pneu_id: str = None, _u: dict = Depends(require("read"))):
    query = {}
    if pneu_id:
        query["pneu_id"] = pneu_id
    docs = await db.pneu_movimentacoes.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return [PneuMovimentacao(**d) for d in docs]

@router.post("", response_model=PneuMovimentacao, status_code=201)
async def criar(body: PneuMovimentacaoCreate, user: dict = Depends(require("write"))):
    # Busca o pneu para validar
    pneu = await db.pneus.find_one({"id": body.pneu_id})
    if not pneu:
        raise HTTPException(404, "Pneu não encontrado.")

    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    doc["created_by"] = user["nome"]

    # Atualiza o status do pneu conforme o tipo de movimentação
    novo_status = pneu.get("status", "Estoque")
    if body.tipo == "APLICACAO":
        novo_status = "Aplicado"
    elif body.tipo == "RODIZIO":
        novo_status = "Aplicado"
    elif body.tipo == "RECAPAGEM":
        novo_status = "Recapagem"
    elif body.tipo == "CONSERTO":
        novo_status = "Conserto"
    elif body.tipo == "DESCARTE":
        novo_status = "Sucateado"

    update_data = {"status": novo_status}
    if body.veiculo_id:
        update_data["veiculo_id"] = body.veiculo_id
        update_data["carreta_id"] = None
    elif body.carreta_id:
        update_data["carreta_id"] = body.carreta_id
        update_data["veiculo_id"] = None
    
    if body.posicao_destino:
        update_data["posicao"] = body.posicao_destino
    elif body.tipo in ["RECAPAGEM", "CONSERTO", "DESCARTE"]:
        update_data["posicao"] = None
        update_data["veiculo_id"] = None
        update_data["carreta_id"] = None

    await db.pneus.update_one({"id": body.pneu_id}, {"$set": update_data})
    await db.pneu_movimentacoes.insert_one(dict(doc))
    
    return PneuMovimentacao(**doc)

@router.get("/{pneu_id}/historico", response_model=list[PneuMovimentacao])
async def historico(pneu_id: str, _u: dict = Depends(require("read"))):
    docs = await db.pneu_movimentacoes.find({"pneu_id": pneu_id}, {"_id": 0}).sort("created_at", -1).to_list(200)
    return [PneuMovimentacao(**d) for d in docs]
