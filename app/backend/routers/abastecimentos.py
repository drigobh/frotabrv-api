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


@router.get("/ultimo-km/{veiculo_id}")
async def ultimo_km(veiculo_id: str, _u: dict = Depends(require("read"))):
    veiculo = await db.veiculos.find_one({"id": veiculo_id})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")
    
    # Busca o último abastecimento registrado para este veículo
    ultimo_abast = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo_id}, 
        sort=[("km", -1)]
    )
    
    km_veiculo = veiculo.get("hodometro_km", 0)
    km_abast = ultimo_abast["km"] if ultimo_abast else 0
    
    # Retorna o maior KM entre o cadastro e o último abastecimento
    return {"ultimo_km": max(km_veiculo, km_abast)}

@router.post("", response_model=Abastecimento, status_code=201)
async def criar(body: AbastecimentoCreate, request: Request, user: dict = Depends(require("write"))):
    veiculo = await db.veiculos.find_one({"id": body.veiculo_id})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")

    # Validação do Hodômetro: não pode ser menor que o último registrado
    ultimo_abast = await db.abastecimentos.find_one(
        {"veiculo_id": body.veiculo_id}, 
        sort=[("km", -1)]
    )
    km_cadastro = veiculo.get("hodometro_km", 0)
    km_ultimo_abast = ultimo_abast["km"] if ultimo_abast else 0
    km_minimo = max(km_cadastro, km_ultimo_abast)

    if body.km < km_minimo:
        raise HTTPException(400, f"O hodômetro informado ({body.km}) é menor que o último registrado ({km_minimo}).")
    
    motorista_label = None
    if body.motorista_id:
        motorista = await db.motoristas.find_one({"id": body.motorista_id})
        if motorista:
            motorista_label = motorista["nome"]

    # Cálculo do KM Rodados: busca o último abastecimento com KM menor que o atual
    anterior = await db.abastecimentos.find_one(
        {"veiculo_id": body.veiculo_id, "km": {"$lt": body.km}},
        sort=[("km", -1)]
    )
    
    # Se não houver abastecimento anterior, usa o hodômetro do cadastro do veículo
    km_anterior = anterior["km"] if anterior else veiculo.get("hodometro_km", 0)
    km_rodados = body.km - km_anterior if km_anterior > 0 else None
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
