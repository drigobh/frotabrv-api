import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_custos_{agora}.zip"
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

def criar_rotas_financeiras(raiz):
    pasta_routers = os.path.join(raiz, "app", "backend", "routers")
    
    # 1. Rota de Abastecimentos
    codigo_abast = '''import uuid
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
'''
    with open(os.path.join(pasta_routers, "abastecimentos.py"), "w", encoding="utf-8") as f:
        f.write(codigo_abast)

    # 2. Rota de Manutenções
    codigo_manut = '''import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from lib.audit import audit
from lib.dates import now_iso
from lib.db import db
from lib.security import require
from models.manutencoes import Manutencao, ManutencaoCreate

router = APIRouter(prefix="/manutencoes", tags=["manutencoes"])

@router.get("", response_model=list[Manutencao])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.manutencoes.find({}, {"_id": 0}).sort("data", -1).to_list(1000)
    return [Manutencao(**d) for d in docs]

@router.post("", response_model=Manutencao, status_code=201)
async def criar(body: ManutencaoCreate, request: Request, user: dict = Depends(require("write"))):
    veiculo = await db.veiculos.find_one({"id": body.veiculo_id})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")

    doc = {
        "id": str(uuid.uuid4()),
        **body.model_dump(),
        "veiculo_label": f"{veiculo['placa']} - {veiculo.get('modelo', '')}",
        "created_by": user["nome"],
        "created_at": now_iso()
    }
    
    await db.manutencoes.insert_one(dict(doc))
    await audit(user, "criar", "manutencoes", doc["id"], f"Veículo: {doc['veiculo_label']}", request)
    return Manutencao(**doc)
'''
    with open(os.path.join(pasta_routers, "manutencoes.py"), "w", encoding="utf-8") as f:
        f.write(codigo_manut)

    print("✅ Rotas de abastecimentos e manutenções criadas.")

def atualizar_dashboard_custos(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "dashboard.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Substitui o cálculo de custos (que estava zerado) por um cálculo real
    alvo = "    custos = [CustoMes(mes=m, combustivel=0, manutencao=0) for m in last_months(6)]"
    novo = '''    # Cálculo real de custos dos últimos 6 meses
    meses = last_months(6)
    custos = []
    for mes in meses:
        # Busca todos os abastecimentos do mês
        abast = await db.abastecimentos.find(
            {"data": {"$regex": f"^{mes}"}}, {"valor_total": 1}
        ).to_list(10000)
        total_combustivel = sum(a.get("valor_total", 0) for a in abast)

        # Busca todas as manutenções do mês
        manut = await db.manutencoes.find(
            {"data": {"$regex": f"^{mes}"}}, {"custo": 1}
        ).to_list(10000)
        total_manutencao = sum(m.get("custo", 0) for m in manut)

        custos.append(CustoMes(mes=mes, combustivel=total_combustivel, manutencao=total_manutencao))'''

    if alvo in conteudo:
        conteudo = conteudo.replace(alvo, novo)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("⚙️ Dashboard atualizado para calcular custos reais.")
    else:
        print("⚠️ Aviso: Linha de custos não encontrada no dashboard. O arquivo pode ser diferente.")

def atualizar_server(raiz):
    caminho = os.path.join(raiz, "app", "backend", "server.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    alvo_import = "from routers import auth, veiculos, carretas, motoristas, dashboard, acoplamentos"
    novo_import = "from routers import auth, veiculos, carretas, motoristas, dashboard, acoplamentos, abastecimentos, manutencoes"
    conteudo = conteudo.replace(alvo_import, novo_import)

    alvo_include = "api_router.include_router(acoplamentos.router)"
    novo_include = "api_router.include_router(acoplamentos.router)\napi_router.include_router(abastecimentos.router)\napi_router.include_router(manutencoes.router)"
    conteudo = conteudo.replace(alvo_include, novo_include)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ server.py atualizado com as rotas de abastecimentos e manutenções.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Custos e Rotas Financeiras...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    criar_rotas_financeiras(raiz)
    atualizar_dashboard_custos(raiz)
    atualizar_server(raiz)

    print("🚀 Automação concluída! Faça o commit e push para o Render.")

if __name__ == "__main__":
    executar()