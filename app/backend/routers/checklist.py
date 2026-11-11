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
