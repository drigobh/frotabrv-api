import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_server_{agora}.zip"
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

def corrigir_server(raiz):
    caminho = os.path.join(raiz, "app", "backend", "server.py")
    
    codigo_novo = '''from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import os
from lib.db import ensure_indexes, client

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_indexes()
    yield
    client.close()

app = FastAPI(title="FrotaBrv API", lifespan=lifespan)

origins = os.environ.get("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")

@api_router.get("/health")
async def health():
    return {"status": "ok", "service": "frota-brv"}

# Importando todas as rotas
from routers import auth, veiculos, carretas, motoristas, dashboard, acoplamentos

api_router.include_router(auth.router)
api_router.include_router(veiculos.router)
api_router.include_router(carretas.router)
api_router.include_router(motoristas.router)
api_router.include_router(dashboard.router)
api_router.include_router(acoplamentos.router)

app.include_router(api_router)
'''
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo_novo)
    print("⚙️ server.py reescrito com sucesso! Todas as rotas foram incluídas.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção do server.py...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    corrigir_server(raiz)

    print("🚀 Automação concluída! Faça o commit e push para o Render.")

if __name__ == "__main__":
    executar()
    