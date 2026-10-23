import os
import re
import datetime
import zipfile

def criar_backup_rapido(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"backup_recriar_final_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        pasta = os.path.join(raiz, "app", "backend")
        for root, dirs, files in os.walk(pasta):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'backups']]
            for file in files:
                c = os.path.join(root, file)
                r = os.path.relpath(c, raiz)
                try: zipf.write(c, r)
                except: pass

def recriar_abastecimentos(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    
    # O arquivo agora NÃO tem prefixo. O prefixo será definido no server.py
    codigo = '''from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from datetime import datetime, timedelta
import uuid

router = APIRouter(tags=["Abastecimentos"])

class AbastecimentoCreate(BaseModel):
    data: str
    veiculo_id: str
    motorista_id: Optional[str] = None
    litros: float
    preco_litro: float
    posto: str
    km: int
    observacoes: Optional[str] = ""
    numero_nf: Optional[str] = None
    chave_nfe: Optional[str] = None
    hora: Optional[str] = None
    cnpj: Optional[str] = None
    fornecedor: Optional[str] = None
    origem: Optional[str] = "manual"

@router.get("")
async def listar_abastecimentos(
    veiculo_id: Optional[str] = Query(None),
    mes: Optional[str] = Query(None),
    user: dict = Depends(require("read"))
):
    query = {}
    if veiculo_id:
        query["veiculo_id"] = veiculo_id
    if mes:
        query["data"] = {"$regex": f"^{mes}"}
        
    dados = await db.abastecimentos.find(query, {"_id": 0}).sort("data", -1).to_list(None)
    return dados

@router.get("/ultimo-km/{veiculo_id}")
async def ultimo_km(veiculo_id: str, user: dict = Depends(require("read"))):
    ultimo = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo_id}, 
        sort=[("data", -1)]
    )
    return {"ultimo_km": ultimo["km"] if ultimo else 0}

@router.post("")
async def criar_abastecimento(payload: AbastecimentoCreate, user: dict = Depends(require("write"))):
    veiculo = await db.veiculos.find_one({"id": payload.veiculo_id})
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado.")
        
    ultimo = await db.abastecimentos.find_one(
        {"veiculo_id": payload.veiculo_id, "data": {"$lt": payload.data}},
        sort=[("data", -1)]
    )
    
    km_rodados = None
    media_km_l = None
    
    if ultimo and ultimo.get("km") and payload.km > ultimo["km"]:
        km_rodados = payload.km - ultimo["km"]
        if payload.litros > 0:
            media_km_l = km_rodados / payload.litros

    doc = payload.dict()
    doc["id"] = str(uuid.uuid4())
    doc["veiculo_label"] = f"{veiculo['placa']} · {veiculo['modelo']}"
    doc["valor_total"] = payload.litros * payload.preco_litro
    doc["km_rodados"] = km_rodados
    doc["media_km_l"] = media_km_l
    doc["created_at"] = now_iso()
    
    if payload.motorista_id:
        mot = await db.motoristas.find_one({"id": payload.motorista_id})
        doc["motorista_label"] = mot["nome"] if mot else None
    else:
        doc["motorista_label"] = None

    await db.abastecimentos.insert_one(doc)
    return doc

@router.post("/importar")
async def importar_abastecimento(payload: dict, user: dict = Depends(require("write"))):
    placa = payload.get("placa")
    if not placa:
        raise HTTPException(status_code=400, detail="Placa não informada.")
        
    veiculo = await db.veiculos.find_one({"placa": placa})
    if not veiculo:
        raise HTTPException(status_code=404, detail=f"Veículo com placa {placa} não encontrado.")

    # Verifica duplicidade
    existe = await db.abastecimentos.find_one({
        "data": payload.get("data"),
        "veiculo_id": veiculo["id"],
        "litros": payload.get("litros")
    })
    if existe:
        raise HTTPException(status_code=400, detail=f"Abastecimento duplicado (Data: {payload.get('data')}, Litros: {payload.get('litros')})")

    ultimo = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo["id"], "data": {"$lt": payload.get("data")}},
        sort=[("data", -1)]
    )

    km_rodados = None
    media_km_l = None

    if ultimo and ultimo.get("km") and payload.get("km"):
        km_rodados = payload.get("km") - ultimo["km"]
        if km_rodados > 0 and payload.get("litros") > 0:
            media_km_l = km_rodados / payload.get("litros")
        else:
            km_rodados = None

    doc = {
        "id": str(uuid.uuid4()),
        "data": payload.get("data"),
        "veiculo_id": veiculo["id"],
        "veiculo_label": f"{veiculo['placa']} · {veiculo['modelo']}",
        "motorista_id": None,
        "motorista_label": None,
        "litros": payload.get("litros"),
        "preco_litro": payload.get("preco_litro"),
        "valor_total": (payload.get("litros") or 0) * (payload.get("preco_litro") or 0),
        "posto": payload.get("fornecedor") or "Importado",
        "km": payload.get("km"),
        "km_rodados": km_rodados,
        "media_km_l": media_km_l,
        "origem": "pdf",
        "numero_nf": payload.get("numero_nf"),
        "chave_nfe": payload.get("chave_nfe"),
        "hora": payload.get("hora"),
        "cnpj": payload.get("cnpj"),
        "fornecedor": payload.get("fornecedor"),
        "created_at": now_iso()
    }

    await db.abastecimentos.insert_one(doc)
    return doc

@router.put("/{id}")
async def atualizar_abastecimento(id: str, payload: AbastecimentoCreate, user: dict = Depends(require("write"))):
    veiculo = await db.veiculos.find_one({"id": payload.veiculo_id})
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado.")
        
    ultimo = await db.abastecimentos.find_one(
        {"veiculo_id": payload.veiculo_id, "data": {"$lt": payload.data}, "id": {"$ne": id}},
        sort=[("data", -1)]
    )
    
    km_rodados = None
    media_km_l = None
    
    if ultimo and ultimo.get("km") and payload.km > ultimo["km"]:
        km_rodados = payload.km - ultimo["km"]
        if payload.litros > 0:
            media_km_l = km_rodados / payload.litros

    doc = payload.dict()
    doc["veiculo_label"] = f"{veiculo['placa']} · {veiculo['modelo']}"
    doc["valor_total"] = payload.litros * payload.preco_litro
    doc["km_rodados"] = km_rodados
    doc["media_km_l"] = media_km_l
    
    if payload.motorista_id:
        mot = await db.motoristas.find_one({"id": payload.motorista_id})
        doc["motorista_label"] = mot["nome"] if mot else None
    else:
        doc["motorista_label"] = None

    await db.abastecimentos.update_one({"id": id}, {"$set": doc})
    doc["id"] = id
    return doc

@router.delete("/{id}")
async def excluir_abastecimento(id: str, user: dict = Depends(require("delete"))):
    await db.abastecimentos.delete_one({"id": id})
    return {"ok": True}

@router.get("/hodometro-atual")
async def get_hodometro_atual(user: dict = Depends(require("read"))):
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
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ abastecimentos.py recriado sem prefixo.")

def verificar_server(raiz):
    caminho = os.path.join(raiz, "app", "backend", "server.py")
    if not os.path.exists(caminho):
        print("❌ server.py não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Verifica se o prefixo está correto no include_router
    if 'app.include_router(abastecimentos.router, prefix="/api/abastecimentos")' not in conteudo:
        print("⚠️ O server.py NÃO tem o prefixo correto. Corrigindo...")
        
        # Remove qualquer include_router antigo de abastecimentos
        conteudo = re.sub(r'app\.include_router\(abastecimentos\.router[^\)]*\)', '', conteudo)
        
        # Adiciona o include_router correto após a declaração do app
        if "app = FastAPI()" in conteudo:
            conteudo = conteudo.replace(
                "app = FastAPI()",
                'app = FastAPI()\napp.include_router(abastecimentos.router, prefix="/api/abastecimentos")'
            )
        else:
            print("❌ Não foi possível encontrar 'app = FastAPI()' no server.py.")

        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ server.py corrigido.")
    else:
        print("✅ O server.py já tem o prefixo correto.")

if __name__ == "__main__":
    raiz = os.getcwd()
    criar_backup_rapido(raiz)
    recriar_abastecimentos(raiz)
    verificar_server(raiz)
    print("\n🚀 Faça o commit e push para o Render.")