import uuid
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Request
from lib.audit import audit
from lib.dates import now_iso
from lib.db import db
from lib.security import require
from models.acoplamentos import Acoplamento, AcoplamentoCreate, HistoricoItem

router = APIRouter(prefix="/acoplamentos", tags=["Acoplamentos"])

async def _get_labels(veiculo_id: str, carreta_id: str | None, motorista_id: str | None) -> tuple[str, str | None, str | None]:
    veiculo = await db.veiculos.find_one({"id": veiculo_id})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")
    v_label = f"{veiculo['placa']} - {veiculo.get('modelo', '')}"
    
    c_label = None
    if carreta_id:
        carreta = await db.carretas.find_one({"id": carreta_id})
        if not carreta:
            raise HTTPException(404, "Carreta não encontrada")
        c_label = f"{carreta['codigo']} - {carreta.get('tipo', '')}"
        
    m_label = None
    if motorista_id:
        motorista = await db.motoristas.find_one({"id": motorista_id})
        if not motorista:
            raise HTTPException(404, "Motorista não encontrado")
        m_label = motorista['nome']

    return v_label, c_label, m_label

@router.get("", response_model=list[Acoplamento])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.acoplamentos.find({"status": "ativo"}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return [Acoplamento(**d) for d in docs]

@router.post("", response_model=Acoplamento, status_code=201)
async def criar(body: AcoplamentoCreate, request: Request, user: dict = Depends(require("write"))):
    # 1. Valida se o veículo já está acoplado
    existente = await db.acoplamentos.find_one({"veiculo_id": body.veiculo_id, "status": "ativo"})
    if existente:
        raise HTTPException(409, "Este veículo já está em um acoplamento ativo.")

    # 2. Busca os labels para salvar no histórico
    v_label, c_label, m_label = await _get_labels(body.veiculo_id, body.carreta_id, body.motorista_id)

    doc = {
        "id": str(uuid.uuid4()),
        "veiculo_id": body.veiculo_id,
        "veiculo_label": v_label,
        "carreta_id": body.carreta_id,
        "carreta_label": c_label,
        "motorista_id": body.motorista_id,
        "motorista_label": m_label,
        "status": "ativo",
        "completo": bool(body.carreta_id and body.motorista_id),
        "created_at": now_iso(),
        "created_by": user["nome"],
        "updated_at": now_iso()
    }
    
    await db.acoplamentos.insert_one(dict(doc))
    
    # 3. Registrar no histórico
    hist_doc = {
        "id": str(uuid.uuid4()),
        "acoplamento_id": doc["id"],
        "conjunto": v_label.split(" ")[0],
        "evento": "Novo Conjunto",
        "item": "conjunto",
        "descricao": f"Criado por {user['nome']}",
        "status": "Acoplado",
        "usuario": user["nome"],
        "created_at": now_iso()
    }
    await db.acoplamentos_historico.insert_one(dict(hist_doc))
    
    await audit(user, "criar", "acoplamentos", doc["id"], f"Veículo: {v_label}", request)
    
    return Acoplamento(**doc)

@router.get("/historico", response_model=list[HistoricoItem])
async def historico(limit: int = 100, _u: dict = Depends(require("read"))):
    docs = await db.acoplamentos_historico.find({}, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return [HistoricoItem(**d) for d in docs]
