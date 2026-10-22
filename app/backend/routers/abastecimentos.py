import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from lib.audit import audit
from lib.dates import now_iso
from lib.db import db
from lib.security import require
from models.abastecimentos import Abastecimento, AbastecimentoCreate

router = APIRouter(prefix="/abastecimentos", tags=["abastecimentos"])

@router.get("", response_model=list[Abastecimento])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.abastecimentos.find({}, {"_id": 0}).sort("data", -1).to_list(1000)
    return [Abastecimento(**d) for d in docs]

@router.post("", response_model=Abastecimento, status_code=201)
async def criar(body: AbastecimentoCreate, request: Request, user: dict = Depends(require("write"))):
    veiculo = await db.veiculos.find_one({"id": body.veiculo_id})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")
    
    motorista_label = None
    if body.motorista_id:
        motorista = await db.motoristas.find_one({"id": body.motorista_id})
        if motorista:
            motorista_label = motorista["nome"]

    # Cálculo do KM Rodados (se houver abastecimento anterior)
    anterior = await db.abastecimentos.find_one(
        {"veiculo_id": body.veiculo_id, "km": {"$lt": body.km}},
        sort=[("km", -1)]
    )
    km_rodados = body.km - anterior["km"] if anterior else None
    media_km_l = km_rodados / body.litros if km_rodados and body.litros > 0 else None
    valor_total = body.litros * body.preco_litro

    doc = {
        "id": str(uuid.uuid4()),
        **body.model_dump(),
        "valor_total": round(valor_total, 2),
        "km_rodados": km_rodados,
        "media_km_l": round(media_km_l, 2) if media_km_l else None,
        "veiculo_label": f"{veiculo['placa']} - {veiculo.get('modelo', '')}",
        "motorista_label": motorista_label,
        "created_by": user["nome"],
        "created_at": now_iso()
    }
    
    await db.abastecimentos.insert_one(dict(doc))
    await audit(user, "criar", "abastecimentos", doc["id"], f"Veículo: {doc['veiculo_label']}", request)
    return Abastecimento(**doc)
