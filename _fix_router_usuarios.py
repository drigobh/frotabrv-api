import os
import re

# 1. Criar o arquivo usuarios.py no backend
path_usuarios = os.path.join(os.getcwd(), "app", "backend", "routers", "usuarios.py")

conteudo = r'''from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require

router = APIRouter()

@router.get("")
async def listar_usuarios(_u: dict = Depends(require("read"))):
    usuarios = await db.usuarios.find({}, {"_id": 0, "senha": 0}).to_list(1000)
    return usuarios

@router.get("/{id}")
async def obter_usuario(id: str, _u: dict = Depends(require("read"))):
    usuario = await db.usuarios.find_one({"id": id}, {"_id": 0, "senha": 0})
    if not usuario:
        raise HTTPException(404, "Usuário não encontrado.")
    return usuario

@router.patch("/{id}/status")
async def alterar_status(id: str, body: dict, _u: dict = Depends(require("write"))):
    ativo = body.get("ativo", True)
    await db.usuarios.update_one({"id": id}, {"$set": {"ativo": ativo}})
    return {"status": "ok"}
'''

with open(path_usuarios, "w", encoding="utf-8") as f:
    f.write(conteudo)
print("✅ Arquivo usuarios.py criado no backend.")

# 2. Registrar o router no server.py
path_server = os.path.join(os.getcwd(), "app", "backend", "server.py")

with open(path_server, "r", encoding="utf-8") as f:
    server_c = f.read()

# Adicionar import
if "import usuarios" not in server_c and "from routers import" not in server_c.split("include_router")[0]:
    # Se o import é do tipo "from routers import ..."
    match_import = re.search(r'from routers import ([^\n]+)', server_c)
    if match_import:
        server_c = server_c.replace(match_import.group(1), match_import.group(1) + ", usuarios")
    
    # Se for do tipo "import routers.usuarios"
    if "import usuarios" not in server_c:
        server_c = server_c.replace(
            "from routers import",
            "from routers import usuarios,"
        )

# Adicionar include_router
if "include_router(usuarios.router)" not in server_c:
    # Tenta achar o include_router do auth para colocar logo depois
    match_auth = re.search(r'api_router\.include_router\(auth\.router\)\n', server_c)
    if match_auth:
        server_c = server_c.replace(match_auth.group(0), match_auth.group(0) + 'api_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])\n')
    else:
        # Coloca no final dos includes
        server_c += '\napi_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])\n'

with open(path_server, "w", encoding="utf-8") as f:
    f.write(server_c)
print("✅ Router usuarios registrado no server.py com prefixo /usuarios.")

# 3. Corrigir o frontend para chamar /usuarios (sem /api extra)
path_front = os.path.join(os.getcwd(), "frontend", "src", "pages", "Usuarios.tsx")

with open(path_front, "r", encoding="utf-8") as f:
    front_c = f.read()

# A URL já está correta na chamada apiGet("/usuarios") pois o api.ts já adiciona /api
# Vamos apenas garantir que não estamos usando "/api/usuarios" duplicado
front_c = front_c.replace('apiGet<any[]>("/api/usuarios")', 'apiGet<any[]>("/usuarios")')
front_c = front_c.replace('apiPatch(`/api/usuarios/', 'apiPatch(`/usuarios/')

with open(path_front, "w", encoding="utf-8") as f:
    f.write(front_c)
print("✅ Frontend ajustado para chamar /usuarios (o api.ts adiciona o /api).")

print("\n✅ Correções aplicadas! Faça o git push para atualizar o Render.")