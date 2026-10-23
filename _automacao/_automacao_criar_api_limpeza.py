import os
import shutil
import datetime
import zipfile

def criar_backup_rapido(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_rapido_api_{agora}.zip"
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print(f"📦 Criando Backup Rápido do Backend...")
    ignorar = ['node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build']
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta_alvo in ['app', 'backend']:
            caminho_pasta = os.path.join(raiz, pasta_alvo)
            if not os.path.exists(caminho_pasta):
                continue
            for root, dirs, files in os.walk(caminho_pasta):
                dirs[:] = [d for d in dirs if d not in ignorar]
                for file in files:
                    caminho_completo = os.path.join(root, file)
                    caminho_relativo = os.path.relpath(caminho_completo, raiz)
                    try:
                        zipf.write(caminho_completo, caminho_relativo)
                    except Exception:
                        pass
    print(f"✅ Backup salvo: {nome_backup}")

def criar_rota_api(raiz):
    pasta_backend = os.path.join(raiz, "app", "backend")
    if not os.path.exists(pasta_backend):
        pasta_backend = os.path.join(raiz, "backend")
        
    pasta_backups_backend = os.path.join(pasta_backend, "backups")
    os.makedirs(pasta_backups_backend, exist_ok=True)
    
    pasta_routers = os.path.join(pasta_backend, "routers")
    os.makedirs(pasta_routers, exist_ok=True)
    
    caminho_admin = os.path.join(pasta_routers, "admin.py")
    
    codigo_admin = '''from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
import json
import os
from datetime import datetime

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.post("/limpar-base")
async def limpar_base(colecao: str, user: dict = Depends(require("admin"))):
    # Lista de coleções permitidas para evitar injeção de nomes maliciosos
    colecoes_permitidas = ["veiculos", "carretas", "motoristas", "acoplamentos", "abastecimentos"]
    
    if colecao not in colecoes_permitidas:
        raise HTTPException(status_code=400, detail="Coleção inválida ou não permitida para limpeza.")
    
    # 1. Backup Automático no Backend
    dados = await db[colecao].find({}, {"_id": 0}).to_list(None)
    nome_arquivo = None
    
    if dados:
        pasta_backup = os.path.join(os.getcwd(), "backups")
        os.makedirs(pasta_backup, exist_ok=True)
        nome_arquivo = f"backup_{colecao}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        caminho_arquivo = os.path.join(pasta_backup, nome_arquivo)
        
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2, default=str)
            
        print(f"Backup salvo em: {caminho_arquivo}")

    # 2. Apaga os dados da coleção
    result = await db[colecao].delete_many({})
    
    return {
        "mensagem": f"Base da coleção '{colecao}' limpa com sucesso.",
        "quantidade_apagada": result.deleted_count,
        "backup": nome_arquivo if dados else None
    }
'''
    
    with open(caminho_admin, 'w', encoding='utf-8') as f:
        f.write(codigo_admin)
    print(f"✅ Arquivo routers/admin.py criado em {pasta_routers}")

    caminho_server = os.path.join(pasta_backend, "server.py")
    if os.path.exists(caminho_server):
        with open(caminho_server, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            
        if "from routers import admin" not in conteudo:
            conteudo = conteudo.replace(
                "from lib.db import db",
                "from lib.db import db\nfrom routers import admin"
            )
            if "app.include_router(admin.router)" not in conteudo:
                conteudo = conteudo.replace(
                    "app = FastAPI()",
                    "app = FastAPI()\napp.include_router(admin.router)"
                )
            with open(caminho_server, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            print("✅ Router 'admin' registrado no server.py.")
        else:
            print("ℹ️ Router 'admin' já estava registrado no server.py.")
    else:
        print("⚠️ Arquivo server.py não encontrado. Registre o router manualmente.")

if __name__ == "__main__":
    raiz = os.getcwd()
    criar_backup_rapido(raiz)
    criar_rota_api(raiz)