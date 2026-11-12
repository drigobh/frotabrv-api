from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import uuid
from models.orcamentos import OrcamentoCreate
from lib.db import db
from .auth import require

router = APIRouter(prefix="/orcamentos", tags=["Orçamentos"])

async def gerar_numero_orcamento():
    res = await db.contadores.find_one_and_update(
        {"_id": "orcamentos"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    seq = res.get("seq", 1) if res else 1
    return f"ORC-{seq:04d}"

@router.post("")
async def criar_orcamento(payload: OrcamentoCreate, _u: dict = Depends(require("write"))):
    try:
        doc = {
            "id": str(uuid.uuid4()),
            "numero": await gerar_numero_orcamento(),
            "fornecedor_id": payload.fornecedor_id,
            "fornecedor_nome_ia": payload.fornecedor_nome_ia,
            "itens": [item.model_dump() for item in payload.itens],
            "observacoes": payload.observacoes,
            "origem": payload.origem,
            "status": "Pendente",
            "data_criacao": datetime.now().isoformat(),
            "criado_por": _u.get("nome", "Sistema")
        }
        await db.orcamentos.insert_one(doc)
        doc.pop("_id", None)
        return doc
    except Exception as e:
        raise HTTPException(400, f"Erro ao criar orçamento: {str(e)}")

@router.get("")
async def listar_orcamentos(_u: dict = Depends(require("read"))):
    return await db.orcamentos.find({}, {"_id": 0}).sort("data_criacao", -1).to_list(1000)

# ROTA SIMULADA DE IA (Fase 3)
@router.post("/ia-search")
async def ia_search(payload: dict, _u: dict = Depends(require("read"))):
    produto = payload.get("produto", "").lower()
    cidade = payload.get("cidade", "")
    estado = payload.get("estado", "")
    
    # Simulação de resposta da IA com preços e fornecedores
    resultados = [
        {"fornecedor": "Auto Peças Silva", "cnpj": "12.345.678/0001-90", "preco": 120.50, "cidade": f"{cidade} - {estado}", "origem": "IA"},
        {"fornecedor": "Distribuidora ABC", "cnpj": "98.765.432/0001-10", "preco": 115.00, "cidade": f"{cidade} - {estado}", "origem": "IA"},
        {"fornecedor": "Atacadão das Peças", "cnpj": "45.678.901/0001-23", "preco": 130.00, "cidade": f"{cidade} - {estado}", "origem": "IA"},
    ]
    return resultados
