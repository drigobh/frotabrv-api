import os
import re
import datetime
import zipfile

def criar_backup_rapido(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"backup_recriar_server_{agora}.zip")
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

def recriar_server(raiz):
    caminho = os.path.join(raiz, "app", "backend", "server.py")
    
    if not os.path.exists(caminho):
        print("❌ server.py não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo_antigo = f.read()

    # Extrai todos os imports de routers que já existiam
    # Ex: from routers import auth, veiculos, carretas, motoristas, dashboard, acoplamentos, abastecimentos, manutencoes
    match_import = re.search(r'from routers import (.*)', conteudo_antigo)
    if match_import:
        routers_existentes = match_import.group(1).replace(" ", "").split(",")
    else:
        routers_existentes = ["auth", "veiculos", "carretas", "motoristas", "dashboard", "acoplamentos", "abastecimentos", "manutencoes"]

    # Garante que 'abastecimentos' e 'admin' estão na lista
    if "abastecimentos" not in routers_existentes:
        routers_existentes.append("abastecimentos")
    if "admin" not in routers_existentes:
        routers_existentes.append("admin")

    # Monta a string de import
    import_routers = f"from routers import {', '.join(routers_existentes)}\n"

    # Monta o código novo do server.py
    codigo_novo = f'''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from lib.db import db
{import_routers}
from lib.security import hash_password
import os

app = FastAPI(title="FrotaBravus API")

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://frotabrv-api.onrender.com", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro das rotas com prefixos corretos
'''
    
    # Adiciona cada router com seu prefixo
    prefixos = {
        "auth": "/api/auth",
        "veiculos": "/api/veiculos",
        "carretas": "/api/carretas",
        "motoristas": "/api/motoristas",
        "dashboard": "/api/dashboard",
        "acoplamentos": "/api/acoplamentos",
        "abastecimentos": "/api/abastecimentos",
        "manutencoes": "/api/manutencoes",
        "admin": "/api/admin"
    }

    for router in routers_existentes:
        if router in prefixos:
            codigo_novo += f'app.include_router({router}.router, prefix="{prefixos[router]}")\n'
        else:
            # Se for um router novo que não está no dicionário, tenta usar o próprio nome como prefixo
            codigo_novo += f'app.include_router({router}.router, prefix="/api/{router}")\n'

    # Adiciona rotas de healthcheck ou outras se existirem
    if "@app.get(" in conteudo_antigo:
        # Extrai rotas avulsas (fora de routers) do arquivo antigo
        rotas_avulsas = re.findall(r'@app\.(get|post|put|delete)\([^)]+\).*?(?=@app\.|\Z)', conteudo_antigo, re.DOTALL)
        for rota in rotas_avulsas:
            codigo_novo += f"\n{rota.strip()}\n"

    codigo_novo += '''
@app.on_event("startup")
async def startup():
    print("✅ API Iniciada com sucesso!")

@app.on_event("shutdown")
async def shutdown():
    print("🛑 API Finalizada.")
'''

    # Salva o novo arquivo
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo_novo)
    print("✅ server.py recriado com sucesso com todos os prefixos!")

if __name__ == "__main__":
    raiz = os.getcwd()
    criar_backup_rapido(raiz)
    recriar_server(raiz)
    print("\n🚀 Faça o commit e push para o Render.")