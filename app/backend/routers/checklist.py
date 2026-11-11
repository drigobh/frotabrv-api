from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import uuid
from models.checklist import ChecklistViagemCreate
from lib.db import db
from .auth import require

router = APIRouter(prefix="/checklist", tags=["Checklist"])

@router.post("")
async def criar_checklist(payload: ChecklistViagemCreate, _u: dict = Depends(require("write"))):
    try:
        doc = {
            "id": str(uuid.uuid4()),
            "veiculo_id": payload.veiculo_id,
            "motorista_id": payload.motorista_id,
            "itens": [item.model_dump() for item in payload.itens],
            "observacoes_gerais": payload.observacoes_gerais,
            "status_geral": payload.status_geral,
            "data_criacao": datetime.now().isoformat(),
            "criado_por": _u.get("nome", "Sistema")
        }
        await db.checklists.insert_one(doc)
        doc.pop("_id", None)
        return doc
    except Exception as e:
        raise HTTPException(400, f"Erro ao salvar checklist: {str(e)}")

@router.get("/veiculo/{veiculo_id}")
async def listar_por_veiculo(veiculo_id: str, _u: dict = Depends(require("read"))):
    return await db.checklists.find({"veiculo_id": veiculo_id}, {"_id": 0}).sort("data_criacao", -1).to_list(100)


@router.get("")
async def listar_checklists(
    data_inicio: str = None,
    data_fim: str = None,
    motorista_id: str = None,
    veiculo_id: str = None,
    _u: dict = Depends(require("read"))
):
    filtro = {}
    if data_inicio and data_fim:
        filtro["data_criacao"] = {"$gte": data_inicio, "$lte": data_fim}
    if motorista_id:
        filtro["motorista_id"] = motorista_id
    if veiculo_id:
        filtro["veiculo_id"] = veiculo_id
    
    return await db.checklists.find(filtro, {"_id": 0}).sort("data_criacao", -1).to_list(1000)
