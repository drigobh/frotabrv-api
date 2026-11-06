import os
import re

# 1. Criar o router de cadastros financeiros
path_fin = os.path.join(os.getcwd(), "app", "backend", "routers", "cadastros_financeiros.py")

conteudo = r'''from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from datetime import datetime
import uuid

router = APIRouter()

# --- BANCOS ---
@router.get("/bancos")
async def listar_bancos(_u: dict = Depends(require("read"))):
    return await db.bancos.find({}, {"_id": 0}).to_list(100)

@router.post("/bancos")
async def criar_banco(body: dict, _u: dict = Depends(require("write"))):
    novo = {"id": str(uuid.uuid4()), "nome": body.get("nome"), "agencia": body.get("agencia", ""), "conta": body.get("conta", ""), "saldo_inicial": float(body.get("saldo_inicial", 0))}
    await db.bancos.insert_one(novo)
    novo.pop("_id", None)
    return novo

# --- CATEGORIAS FINANCEIRAS ---
@router.get("/categorias")
async def listar_categorias(tipo: str = None, _u: dict = Depends(require("read"))):
    filtro = {}
    if tipo:
        filtro["tipo"] = tipo
    return await db.categorias_financeiras.find(filtro, {"_id": 0}).to_list(100)

@router.post("/categorias")
async def criar_categoria(body: dict, _u: dict = Depends(require("write"))):
    novo = {"id": str(uuid.uuid4()), "nome": body.get("nome"), "tipo": body.get("tipo", "Ambos")}
    await db.categorias_financeiras.insert_one(novo)
    novo.pop("_id", None)
    return novo
'''

with open(path_fin, "w", encoding="utf-8") as f:
    f.write(conteudo)
print("✅ Backend: Router de cadastros financeiros criado.")

# 2. Registrar no server.py
path_server = os.path.join(os.getcwd(), "app", "backend", "server.py")
with open(path_server, "r", encoding="utf-8") as f:
    s_c = f.read()

if "cadastros_financeiros" not in s_c:
    match_import = re.search(r'from routers import ([^\n]+)', s_c)
    if match_import:
        s_c = s_c.replace(match_import.group(1), match_import.group(1) + ", cadastros_financeiros")
    
    match_include = re.search(r'api_router\.include_router\(financeiro\.router[^\n]*\n', s_c)
    if match_include:
        s_c = s_c.replace(match_include.group(0), match_include.group(0) + 'api_router.include_router(cadastros_financeiros.router, prefix="/cadastros-financeiros", tags=["cadastros-financeiros"])\n')
    else:
        s_c += '\napi_router.include_router(cadastros_financeiros.router, prefix="/cadastros-financeiros", tags=["cadastros-financeiros"])\n'
    
    with open(path_server, "w", encoding="utf-8") as f:
        f.write(s_c)
    print("✅ Server: Router de cadastros financeiros registrado.")