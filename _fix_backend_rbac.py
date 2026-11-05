import os
import re

# ==========================================
# 1. CRIAR ROUTER DE PERFIS (RBAC)
# ==========================================
path_perfis = os.path.join(os.getcwd(), "app", "backend", "routers", "perfis.py")

conteudo_perfis = r'''from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
import uuid

router = APIRouter()

@router.get("")
async def listar_perfis(_u: dict = Depends(require("read"))):
    return await db.perfis.find({}, {"_id": 0}).to_list(100)

@router.post("")
async def criar_perfil(body: dict, _u: dict = Depends(require("write"))):
    novo = {
        "id": str(uuid.uuid4()),
        "nome": body.get("nome"),
        "descricao": body.get("descricao", ""),
        "permissoes": body.get("permissoes", []),
    }
    await db.perfis.insert_one(novo)
    novo.pop("_id", None)
    return novo

@router.put("/{id}")
async def atualizar_perfil(id: str, body: dict, _u: dict = Depends(require("write"))):
    await db.perfis.update_one({"id": id}, {"$set": body})
    return {"status": "ok"}

@router.delete("/{id}")
async def excluir_perfil(id: str, _u: dict = Depends(require("write"))):
    await db.perfis.delete_one({"id": id})
    return {"status": "ok"}
'''

with open(path_perfis, "w", encoding="utf-8") as f:
    f.write(conteudo_perfis)
print("✅ Backend: Router de perfis criado.")

# ==========================================
# 2. REGISTRAR NO SERVER.PY
# ==========================================
path_server = os.path.join(os.getcwd(), "app", "backend", "server.py")
with open(path_server, "r", encoding="utf-8") as f:
    server_c = f.read()

if "perfis" not in server_c:
    match_import = re.search(r'from routers import ([^\n]+)', server_c)
    if match_import:
        server_c = server_c.replace(match_import.group(1), match_import.group(1) + ", perfis")
    match_include = re.search(r'api_router\.include_router\(usuarios\.router[^\n]*\n', server_c)
    if match_include:
        server_c = server_c.replace(match_include.group(0), match_include.group(0) + 'api_router.include_router(perfis.router, prefix="/perfis", tags=["perfis"])\n')
    with open(path_server, "w", encoding="utf-8") as f:
        f.write(server_c)
    print("✅ Server: Router de perfis registrado.")

# ==========================================
# 3. ATUALIZAR O USUARIOS.PY (NOVOS CAMPOS)
# ==========================================
path_usuarios = os.path.join(os.getcwd(), "app", "backend", "routers", "usuarios.py")
with open(path_usuarios, "r", encoding="utf-8") as f:
    u_c = f.read()

# Adiciona a rota de perfil (PUT /usuarios/{id}/perfil) e campos extras
if "perfil_id" not in u_c:
    u_c = u_c.replace(
        '"perfil": body.get("perfil", "Operador"),',
        '"perfil_id": body.get("perfil_id"),\n        "setor": body.get("setor", ""),\n        "cargo": body.get("cargo", ""),\n        "telefone": body.get("telefone", ""),\n        "whatsapp": body.get("whatsapp", ""),\n        "foto_url": body.get("foto_url", ""),'
    )
    with open(path_usuarios, "w", encoding="utf-8") as f:
        f.write(u_c)
    print("✅ Usuarios.py: Novos campos adicionados (perfil_id, setor, cargo, etc).")

print("\n✅ Backend pronto! Faça o git push.")