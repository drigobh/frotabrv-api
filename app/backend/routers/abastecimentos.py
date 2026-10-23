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
    veiculo = await db.veiculos.find_one({"placa": placa_limpa})
    
    if not veiculo:
        raise HTTPException(404, f"Veículo com placa '{placa_limpa}' não encontrado.")

    acoplamento = await db.acoplamentos.find_one({"veiculo_id": veiculo["id"], "status": "ativo"})
    motorista_label = None
    if acoplamento and acoplamento.get("motorista_id"):
        motorista = await db.motoristas.find_one({"id": acoplamento["motorista_id"]})
        if motorista:
            motorista_label = motorista["nome"]

    km = body.get("km", 0)
    anterior = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo["id"], "km": {"$lt": km}},
        sort=[("km", -1)]
    )
    km_anterior = anterior["km"] if anterior else veiculo.get("hodometro_km", 0)
    km_rodados = km - km_anterior if km_anterior > 0 else None
    
    litros = body.get("litros", 0)
    preco_litro = body.get("preco_litro", 0)
    media_km_l = km_rodados / litros if km_rodados and litros > 0 else None
    valor_total = litros * preco_litro

    doc = {
        "id": str(uuid.uuid4()),
        "data": body.get("data", now_iso()),
        "hora": body.get("hora"),
        "veiculo_id": veiculo["id"],
        "motorista_id": acoplamento.get("motorista_id") if acoplamento else None,
        "motorista_label": motorista_label,
        "litros": litros,
        "preco_litro": preco_litro,
        "posto": body.get("fornecedor", "Importado via PDF"),
        "km": km,
        "observacoes": "",
        "numero_nf": body.get("numero_nf"),
        "chave_nfe": body.get("chave_nfe"),
        "cnpj": body.get("cnpj"),
        "fornecedor": body.get("fornecedor"),
        "origem": "pdf",
        "valor_total": round(valor_total, 2),
        "km_rodados": km_rodados,
        "media_km_l": round(media_km_l, 2) if media_km_l else None,
        "veiculo_label": f"{veiculo['placa']} - {veiculo.get('modelo', '')}",
        "created_by": user["nome"],
        "created_at": now_iso()
    }
    
    await db.abastecimentos.insert_one(dict(doc))
    await audit(user, "importar", "abastecimentos", doc["id"], f"NF: {doc['numero_nf']}", request)
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


@router.get("/hodometro-atual")
async def get_hodometro_atual(user: dict = Depends(require("read"))):
    from datetime import datetime, timedelta
    
    veiculos = await db.veiculos.find({"ativo": True}, {"_id": 0}).to_list(None)
    resultado = []
    
    agora = datetime.now()
    mes_atual = agora.strftime("%Y-%m")
    
    primeiro_dia_mes = agora.replace(day=1)
    ultimo_dia_mes_anterior = primeiro_dia_mes - timedelta(days=1)
    mes_anterior = ultimo_dia_mes_anterior.strftime("%Y-%m")

    for v in veiculos:
        abast = await db.abastecimentos.find({"veiculo_id": v["id"]}).sort("data", 1).to_list(None)
        
        if not abast:
            resultado.append({
                "veiculo_id": v["id"], "placa": v["placa"], "modelo": v["modelo"],
                "ultimo_km": 0, "qtd_geral": 0, "qtd_mes": 0, "qtd_mes_anterior": 0,
                "media_ultimo": 0, "media_mes": 0, "media_mes_anterior": 0,
                "total_mes": 0, "total_mes_anterior": 0, "media_preco_mes": 0
            })
            continue

        ultimo = abast[-1]
        
        abast_mes = [a for a in abast if a["data"].startswith(mes_atual)]
        abast_anterior = [a for a in abast if a["data"].startswith(mes_anterior)]
        
        def calc_media(lista):
            validos = [a for a in lista if a.get("km_rodados") and a.get("km_rodados") > 0]
            if not validos: return 0
            km = sum(a["km_rodados"] for a in validos)
            l = sum(a["litros"] for a in validos)
            return km / l if l > 0 else 0
            
        def calc_total(lista): return sum(a["valor_total"] for a in lista)
        def calc_preco_medio(lista):
            l = sum(a["litros"] for a in lista)
            v = sum(a["valor_total"] for a in lista)
            return v / l if l > 0 else 0

        resultado.append({
            "veiculo_id": v["id"], "placa": v["placa"], "modelo": v["modelo"],
            "ultimo_km": ultimo["km"],
            "qtd_geral": len(abast), "qtd_mes": len(abast_mes), "qtd_mes_anterior": len(abast_anterior),
            "media_ultimo": ultimo.get("media_km_l") or 0,
            "media_mes": calc_media(abast_mes), "media_mes_anterior": calc_media(abast_anterior),
            "total_mes": calc_total(abast_mes), "total_mes_anterior": calc_total(abast_anterior),
            "media_preco_mes": calc_preco_medio(abast_mes)
        })
    return resultado
