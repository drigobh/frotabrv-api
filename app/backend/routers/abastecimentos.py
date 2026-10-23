import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from lib.dates import now_iso
from lib.db import db
from lib.security import require
from models.abastecimentos import Abastecimento, AbastecimentoCreate

router = APIRouter(prefix="/abastecimentos", tags=["abastecimentos"])

@router.get("", response_model=None)
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.abastecimentos.find({}, {"_id": 0}).sort("data", -1).to_list(2000)
    return docs

@router.get("/ultimo-km/{veiculo_id}")
async def ultimo_km(veiculo_id: str, _u: dict = Depends(require("read"))):
    veiculo = await db.veiculos.find_one({"id": veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")
    
    ultimo_abast = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo_id}, 
        {"_id": 0},
        sort=[("km", -1)]
    )
    
    km_veiculo = veiculo.get("hodometro_km", 0)
    km_abast = ultimo_abast["km"] if ultimo_abast else 0
    
    return {"ultimo_km": max(km_veiculo, km_abast)}

@router.post("/importar", response_model=None, status_code=201)
async def importar_pdf(body: dict, request: Request, user: dict = Depends(require("write"))):
    placa_limpa = body.get("placa", "").strip().upper()
    
    veiculo = await db.veiculos.find_one({"placa": placa_limpa}, {"_id": 0})
    if not veiculo:
        raise HTTPException(status_code=404, detail=f"Veículo com placa {placa_limpa} não encontrado.")

    # O Frontend já envia litros e preco_litro divididos corretamente.
    litros = body.get("litros") or 0
    preco_litro = body.get("preco_litro") or 0
    data_abast = body.get("data")

    # Busca o último abastecimento ANTES da data atual para calcular os KM rodados
    ultimo = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo["id"], "data": {"$lt": data_abast}},
        {"_id": 0},
        sort=[("data", -1)]
    )

    km_rodados = None
    media_km_l = None

    # Se tiver um abastecimento anterior, usa a Leitura dele. Senão, usa o Hodômetro Inicial do Veículo.
    if ultimo and ultimo.get("km") and body.get("km"):
        km_rodados = body.get("km") - ultimo["km"]
        if km_rodados > 0 and litros > 0:
            media_km_l = km_rodados / litros
        else:
            km_rodados = None
    elif body.get("km") and veiculo.get("hodometro_km"):
        # Primeiro abastecimento: usa o Hodômetro Inicial do Veículo
        km_rodados = body.get("km") - veiculo["hodometro_km"]
        if km_rodados > 0 and litros > 0:
            media_km_l = km_rodados / litros
        else:
            km_rodados = None

    valor_total = litros * preco_litro

    # Busca o acoplamento ativo para pegar o motorista
    acoplamento = await db.acoplamentos.find_one(
        {"veiculo_id": veiculo["id"], "ativo": True},
        {"_id": 0}
    )
    motorista_id = acoplamento.get("motorista_id") if acoplamento else None
    motorista_label = None
    if motorista_id:
        mot = await db.motoristas.find_one({"id": motorista_id}, {"_id": 0})
        motorista_label = mot["nome"] if mot else None

    doc = {
        "id": str(uuid.uuid4()),
        "data": data_abast,
        "veiculo_id": veiculo["id"],
        "veiculo_label": f"{veiculo['placa']} · {veiculo['modelo']}",
        "motorista_id": motorista_id,
        "motorista_label": motorista_label,
        "litros": litros,
        "preco_litro": preco_litro,
        "valor_total": valor_total,
        "posto": body.get("fornecedor") or "Importado",
        "km": body.get("km"),
        "km_rodados": km_rodados,
        "media_km_l": media_km_l,
        "origem": "excel",
        "numero_nf": body.get("numero_nf"),
        "chave_nfe": body.get("chave_nfe"),
        "hora": body.get("hora"),
        "cnpj": body.get("cnpj"),
        "fornecedor": body.get("fornecedor"),
        "created_by": user.get("id", "sistema"),
        "created_at": now_iso()
    }

    await db.abastecimentos.insert_one(doc)
    doc.pop("_id", None)
    return doc

@router.post("", response_model=Abastecimento, status_code=201)
async def criar(body: AbastecimentoCreate, request: Request, user: dict = Depends(require("write"))):
    veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")

    ultimo = await db.abastecimentos.find_one(
        {"veiculo_id": body.veiculo_id, "data": {"$lt": body.data}},
        {"_id": 0},
        sort=[("data", -1)]
    )

    km_rodados = None
    media_km_l = None

    if ultimo and ultimo.get("km") and body.km > ultimo["km"]:
        km_rodados = body.km - ultimo["km"]
        if body.litros > 0:
            media_km_l = km_rodados / body.litros

    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["veiculo_label"] = f"{veiculo['placa']} · {veiculo['modelo']}"
    doc["motorista_label"] = None
    doc["valor_total"] = body.litros * body.preco_litro
    doc["km_rodados"] = km_rodados
    doc["media_km_l"] = media_km_l
    doc["created_by"] = user["id"]
    doc["created_at"] = now_iso()

    await db.abastecimentos.insert_one(doc)
    doc.pop("_id", None)
    return doc
