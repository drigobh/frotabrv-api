import os
import datetime
import zipfile

def criar_backup_rapido(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_rapido_api_admin_{agora}.zip"
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print("📦 Criando Backup Rápido...")
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        pastas = ['app', 'backend']
        for pasta in pastas:
            caminho_pasta = os.path.join(raiz, pasta)
            if not os.path.exists(caminho_pasta):
                continue
            for root, dirs, files in os.walk(caminho_pasta):
                dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', 'build', '__pycache__']]
                for file in files:
                    caminho_completo = os.path.join(root, file)
                    caminho_relativo = os.path.relpath(caminho_completo, raiz)
                    try:
                        zipf.write(caminho_completo, caminho_relativo)
                    except Exception:
                        pass
    print(f"✅ Backup salvo: {nome_backup}")

def corrigir_backend(raiz):
    # 1. Encontra a pasta do backend
    pasta_backend = os.path.join(raiz, "app", "backend")
    if not os.path.exists(pasta_backend):
        pasta_backend = os.path.join(raiz, "backend")
    
    if not os.path.exists(pasta_backend):
        print("❌ Pasta do backend não encontrada.")
        return

    pasta_routers = os.path.join(pasta_backend, "routers")
    os.makedirs(pasta_routers, exist_ok=True)

    # 2. Cria o arquivo admin.py
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
    colecoes_permitidas = ["veiculos", "carretas", "motoristas", "acoplamentos", "abastecimentos"]
    
    if colecao not in colecoes_permitidas:
        raise HTTPException(status_code=400, detail="Coleção inválida.")
    
    # Backup automático
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

    result = await db[colecao].delete_many({})
    
    return {
        "mensagem": f"Base da coleção '{colecao}' limpa com sucesso.",
        "quantidade_apagada": result.deleted_count,
        "backup": nome_arquivo if dados else None
    }
'''
    with open(caminho_admin, 'w', encoding='utf-8') as f:
        f.write(codigo_admin)
    print("✅ Arquivo routers/admin.py criado/sobrescrito.")

    # 3. Registra no server.py
    caminho_server = os.path.join(pasta_backend, "server.py")
    if os.path.exists(caminho_server):
        with open(caminho_server, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            
        # Verifica se o import já existe
        if "from routers import admin" not in conteudo:
            # Tenta adicionar o import
            conteudo = conteudo.replace(
                "from lib.db import db",
                "from lib.db import db\nfrom routers import admin"
            )
            print("✅ Import do router admin adicionado.")

        # Verifica se o include_router já existe
        if "app.include_router(admin.router)" not in conteudo:
            # Tenta adicionar o include_router
            if "app = FastAPI()" in conteudo:
                conteudo = conteudo.replace(
                    "app = FastAPI()",
                    "app = FastAPI()\napp.include_router(admin.router)"
                )
                print("✅ include_router adicionado.")
            else:
                print("⚠️ Não foi possível encontrar 'app = FastAPI()' no server.py. O include_router pode não estar registrado.")

        with open(caminho_server, 'w', encoding='utf-8') as f:
            f.write(conteudo)
    else:
        print("❌ Arquivo server.py não encontrado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    print("🤖 Iniciando Correção da API Admin no Backend...")
    criar_backup_rapido(raiz)
    corrigir_backend(raiz)
    print("\n🚀 Concluído! Reinicie o servidor backend para testar.")