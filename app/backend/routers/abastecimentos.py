import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from lib.audit import audit
from lib.dates import now_iso
from lib.db import db
from lib.security import require
from models.abastecimentos import Abastecimento, AbastecimentoCreate

router = APIRouter(prefix="/abastecimentos", tags=["abastecimentos"])

@router.get("", response_model=None)
async def listar(_u: dict = Depends(require("read"))):
    # Retorna os dados brutos do banco para evitar erros de validação com dados antigos
    docs = await db.abastecimentos.find({}, {"_id": 0}).sort("data", -1).to_list(1000)
    return docs

@router.get("/ultimo-km/{veiculo_id}")
async def ultimo_km(veiculo_id: str, _u: dict = Depends(require("read"))):
    veiculo = await db.veiculos.find_one({"id": veiculo_id})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")
    
    ultimo_abast = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo_id}, 
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

    # O Frontend já envia os valores corrigidos (divididos por 1000 e 100)
    litros_corrigidos = body.get("litros") or 0
    preco_corrigido = body.get("preco_litro") or 0

    ultimo = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo["id"], "data": {"$lt": body.get("data")}},
        {"_id": 0},
        sort=[("data", -1)]
    )

    km_rodados = None
    media_km_l = None

    if ultimo and ultimo.get("km") and body.get("km"):
        km_rodados = body.get("km") - ultimo["km"]
        if km_rodados > 0 and litros_corrigidos > 0:
            media_km_l = km_rodados / litros_corrigidos
        else:
            km_rodados = None

    valor_total = litros_corrigidos * preco_corrigido

    doc = {
        "id": str(uuid.uuid4()),
        "data": body.get("data"),
        "veiculo_id": veiculo["id"],
        "veiculo_label": f"{veiculo['placa']} · {veiculo['modelo']}",
        "motorista_id": None,
        "motorista_label": None,
        "litros": litros_corrigidos,
        "preco_litro": preco_corrigido,
        "valor_total": valor_total,
        "posto": body.get("fornecedor") or "Importado",
        "km": body.get("km"),
        "km_rodados": km_rodados,
        "media_km_l": media_km_l,
        "origem": "pdf",
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
    veiculo = await db.veiculos.find_one({"id": body.veiculo_id})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")
    
    motorista_label = None
    if body.motorista_id:
        motorista = await db.motoristas.find_one({"id": body.motorista_id})
        if motorista:
            motorista_label = motorista["nome"]

    anterior = await db.abastecimentos.find_one(
        {"veiculo_id": body.veiculo_id, "km": {"$lt": body.km}},
        sort=[("km", -1)]
    )
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
        "created_by": user.get("id", "sistema"),
        "created_at": now_iso()
    }
    
    await db.abastecimentos.insert_one(dict(doc))
    await audit(user, "criar", "abastecimentos", doc["id"], f"Veículo: {doc['veiculo_label']}", request)
    return Abastecimento(**doc)

@router.put("/{abastecimento_id}", response_model=Abastecimento)
async def editar(abastecimento_id: str, body: AbastecimentoCreate, request: Request, user: dict = Depends(require("write"))):
    atual = await db.abastecimentos.find_one({"id": abastecimento_id})
    if not atual:
        raise HTTPException(404, "Abastecimento não encontrado")

    veiculo = await db.veiculos.find_one({"id": body.veiculo_id})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")

    motorista_label = None
    if body.motorista_id:
        motorista = await db.motoristas.find_one({"id": body.motorista_id})
        if motorista:
            motorista_label = motorista["nome"]

    anterior = await db.abastecimentos.find_one(
        {"veiculo_id": body.veiculo_id, "km": {"$lt": body.km}, "id": {"$ne": abastecimento_id}},
        sort=[("km", -1)]
    )
    km_anterior = anterior["km"] if anterior else veiculo.get("hodometro_km", 0)
    km_rodados = body.km - km_anterior if km_anterior > 0 else None
    media_km_l = km_rodados / body.litros if km_rodados and body.litros > 0 else None
    valor_total = body.litros * body.preco_litro

    dados_atualizados = {
        **body.model_dump(),
        "valor_total": round(valor_total, 2),
        "km_rodados": km_rodados,
        "media_km_l": round(media_km_l, 2) if media_km_l else None,
        "veiculo_label": f"{veiculo['placa']} - {veiculo.get('modelo', '')}",
        "motorista_label": motorista_label,
    }

    await db.abastecimentos.update_one({"id": abastecimento_id}, {"$set": dados_atualizados})
    await audit(user, "editar", "abastecimentos", abastecimento_id, f"Veículo: {dados_atualizados['veiculo_label']}", request)
    
    doc_atualizado = await db.abastecimentos.find_one({"id": abastecimento_id}, {"_id": 0})
    return Abastecimento(**doc_atualizado)

@router.delete("/{abastecimento_id}", status_code=204)
async def excluir(abastecimento_id: str, request: Request, user: dict = Depends(require("write"))):
    atual = await db.abastecimentos.find_one({"id": abastecimento_id})
    if not atual:
        raise HTTPException(404, "Abastecimento não encontrado")
    
    await db.abastecimentos.delete_one({"id": abastecimento_id})
    await audit(user, "excluir", "abastecimentos", abastecimento_id, f"Veículo: {atual.get('veiculo_label')}", request)
    return None
