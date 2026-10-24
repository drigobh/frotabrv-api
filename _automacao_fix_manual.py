import os

def fix_models(raiz):
    caminho = os.path.join(raiz, "app", "backend", "models", "abastecimentos.py")
    codigo = '''from typing import Literal
from pydantic import BaseModel, Field

class AbastecimentoCreate(BaseModel):
    data: str = Field(pattern=r"^\\d{4}-\\d{2}-\\d{2}$")
    veiculo_id: str
    motorista_id: str | None = None
    combustivel_id: str | None = None
    produto: str | None = None
    litros: float = Field(gt=0)
    preco_litro: float = Field(gt=0)
    posto: str = Field(min_length=1)
    km: float = Field(ge=0)
    observacoes: str = ""
    numero_nf: str | None = None
    chave_nfe: str | None = None
    hora: str | None = None
    cnpj: str | None = None
    fornecedor: str | None = None
    origem: Literal["manual", "pdf", "excel"] = "manual"

class Abastecimento(AbastecimentoCreate):
    id: str
    valor_total: float
    km_rodados: float | None = None
    media_km_l: float | None = None
    veiculo_label: str
    motorista_label: str | None = None
    created_by: str
    created_at: str
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Modelo AbastecimentoCreate atualizado.")

def fix_router(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    codigo = '''from fastapi import APIRouter, Depends, HTTPException, Request
from lib.dates import now_iso
from lib.db import db
from lib.security import require
from models.abastecimentos import Abastecimento, AbastecimentoCreate
import uuid
from datetime import datetime

router = APIRouter(prefix="/abastecimentos", tags=["abastecimentos"])

@router.get("", response_model=None)
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.abastecimentos.find({}, {"_id": 0}).sort("data", -1).to_list(5000)
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

    litros = body.get("litros") or 0
    preco_litro = body.get("preco_litro") or 0
    data_recebida = body.get("data")
    km_atual = body.get("km") or 0
    produto = body.get("produto", "DIESEL").upper()

    try:
        if "/" in data_recebida:
            data_abast = datetime.strptime(data_recebida, "%d/%m/%Y").strftime("%Y-%m-%d")
        else:
            data_abast = data_recebida
    except:
        data_abast = data_recebida

    ultimo = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo["id"], "data": {"$lt": data_abast}},
        {"_id": 0},
        sort=[("data", -1)]
    )

    km_rodados = None
    media_km_l = None

    if ultimo and ultimo.get("km"):
        km_rodados = km_atual - ultimo["km"]
        if km_rodados < 0 or km_rodados > 5000:
            km_rodados = None
    
    if km_rodados and km_rodados > 0 and litros > 0 and "ARLA" not in produto:
        media_km_l = km_rodados / litros

    valor_total = body.get("valor_total")
    if not valor_total:
        valor_total = litros * preco_litro
    valor_total = round(valor_total, 2)

    acoplamento = await db.acoplamentos.find_one(
        {"veiculo_id": veiculo["id"]},
        {"_id": 0},
        sort=[("created_at", -1)]
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
        "km": km_atual,
        "km_rodados": km_rodados,
        "media_km_l": media_km_l,
        "origem": body.get("origem", "excel"),
        "produto": produto,
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

    # Converte a data (YYYY-MM-DD do input date) para manter o padrão
    ultimo = await db.abastecimentos.find_one(
        {"veiculo_id": body.veiculo_id, "data": {"$lt": body.data}},
        {"_id": 0},
        sort=[("data", -1)]
    )

    km_rodados = None
    media_km_l = None

    if ultimo and ultimo.get("km") and body.km > ultimo["km"]:
        km_rodados = body.km - ultimo["km"]
        if body.litros > 0 and "ARLA" not in (body.produto or "").upper():
            media_km_l = km_rodados / body.litros

    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["veiculo_label"] = f"{veiculo['placa']} · {veiculo['modelo']}"
    doc["valor_total"] = round(body.litros * body.preco_litro, 2)
    doc["km_rodados"] = km_rodados
    doc["media_km_l"] = media_km_l
    doc["created_by"] = user["id"]
    doc["created_at"] = now_iso()

    if body.motorista_id:
        mot = await db.motoristas.find_one({"id": body.motorista_id}, {"_id": 0})
        doc["motorista_label"] = mot["nome"] if mot else None
    else:
        doc["motorista_label"] = None
        
    if body.combustivel_id and not body.produto:
        comb = await db.combustiveis.find_one({"id": body.combustivel_id}, {"_id": 0})
        doc["produto"] = comb["nome"] if comb else "Diesel S-10"

    await db.abastecimentos.insert_one(doc)
    doc.pop("_id", None)
    return doc

@router.put("/{id}", response_model=Abastecimento)
async def atualizar(id: str, body: AbastecimentoCreate, request: Request, user: dict = Depends(require("write"))):
    veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")
        
    ultimo = await db.abastecimentos.find_one(
        {"veiculo_id": body.veiculo_id, "data": {"$lt": body.data}, "id": {"$ne": id}},
        {"_id": 0},
        sort=[("data", -1)]
    )
    
    km_rodados = None
    media_km_l = None
    
    if ultimo and ultimo.get("km") and body.km > ultimo["km"]:
        km_rodados = body.km - ultimo["km"]
        if body.litros > 0 and "ARLA" not in (body.produto or "").upper():
            media_km_l = km_rodados / body.litros

    doc = body.model_dump()
    doc["veiculo_label"] = f"{veiculo['placa']} · {veiculo['modelo']}"
    doc["valor_total"] = round(body.litros * body.preco_litro, 2)
    doc["km_rodados"] = km_rodados
    doc["media_km_l"] = media_km_l
    
    if body.motorista_id:
        mot = await db.motoristas.find_one({"id": body.motorista_id}, {"_id": 0})
        doc["motorista_label"] = mot["nome"] if mot else None
    else:
        doc["motorista_label"] = None
        
    if body.combustivel_id and not body.produto:
        comb = await db.combustiveis.find_one({"id": body.combustivel_id}, {"_id": 0})
        doc["produto"] = comb["nome"] if comb else "Diesel S-10"

    await db.abastecimentos.update_one({"id": id}, {"$set": doc})
    doc["id"] = id
    doc["created_by"] = user["id"]
    doc["created_at"] = now_iso()
    return doc

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    await db.abastecimentos.delete_one({"id": id})
    return {"ok": True}
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Router de abastecimentos recriado com as rotas POST, PUT e DELETE.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_models(raiz)
    fix_router(raiz)