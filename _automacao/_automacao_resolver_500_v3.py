import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_500_v3_{agora}.zip"
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print(f"📦 Criando Backup Full do Sistema...")
    ignorar = ['node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build']
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta_alvo in ['app', 'frontend']:
            caminho_pasta = os.path.join(raiz, pasta_alvo)
            for root, dirs, files in os.walk(caminho_pasta):
                dirs[:] = [d for d in dirs if d not in ignorar]
                for file in files:
                    caminho_completo = os.path.join(root, file)
                    caminho_relativo = os.path.relpath(caminho_completo, raiz)
                    try:
                        zipf.write(caminho_completo, caminho_relativo)
                    except Exception:
                        pass
    print(f"✅ Backup Full salvo em: _automacao/backups/{nome_backup}")

def reescrever_abastecimentos(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    
    codigo_novo = '''import uuid
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
'''

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo_novo)
    print("⚙️ Arquivo abastecimentos.py reescrito completamente (GET bruto, POST, PUT, DELETE, IMPORT).")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção DEFINITIVA v3...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    reescrever_abastecimentos(raiz)

    print("\n🚀 Automação concluída! Faça o commit e push para o Render:")
    print("git add .")
    print("git commit -m 'fix: reescrevendo rota de abastecimentos completa'")
    print("git push")

if __name__ == "__main__":
    executar()