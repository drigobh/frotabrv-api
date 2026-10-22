import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_acoplamentos_{agora}.zip"
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

def criar_rota_acoplamentos(raiz):
    pasta_routers = os.path.join(raiz, "app", "backend", "routers")
    
    codigo_router = '''import uuid
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
'''
    
    caminho_arquivo = os.path.join(pasta_routers, "acoplamentos.py")
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write(codigo_router)
    print("✅ Rota de acoplamentos.py criada com sucesso.")

def atualizar_server(raiz):
    caminho_server = os.path.join(raiz, "app", "backend", "server.py")
    with open(caminho_server, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Adiciona o import e a inclusão do router
    alvo = "from routers import auth, veiculos, carretas, motoristas, dashboard"
    novo = "from routers import auth, veiculos, carretas, motoristas, dashboard, acoplamentos"
    conteudo = conteudo.replace(alvo, novo)
    
    alvo_include = "api_router.include_router(dashboard.router)"
    novo_include = "api_router.include_router(dashboard.router)\napi_router.include_router(acoplamentos.router)"
    conteudo = conteudo.replace(alvo_include, novo_include)

    with open(caminho_server, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ server.py atualizado com a rota de acoplamentos!")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Acoplamentos...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    criar_rota_acoplamentos(raiz)
    atualizar_server(raiz)

    print("🚀 Automação concluída! Faça o commit e push para o Render.")

if __name__ == "__main__":
    executar()