from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.fornecedores import Fornecedor, FornecedorCreate
import uuid

router = APIRouter(prefix="/fornecedores", tags=["fornecedores"])

@router.get("", response_model=list[Fornecedor])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.fornecedores.find({}, {"_id": 0}).sort("nome", 1).to_list(2000)
    return docs

@router.post("", response_model=Fornecedor, status_code=201)
async def criar(body: FornecedorCreate, _u: dict = Depends(require("write"))):
    if body.documento and await db.fornecedores.find_one({"documento": body.documento}):
        raise HTTPException(409, "Fornecedor com este documento já cadastrado")
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    await db.fornecedores.insert_one(doc)
    return doc

@router.put("/{id}", response_model=Fornecedor)
async def atualizar(id: str, body: FornecedorCreate, _u: dict = Depends(require("write"))):
    existe = await db.fornecedores.find_one({"id": id})
    if not existe:
        raise HTTPException(404, "Fornecedor não encontrado")
    if await db.fornecedores.find_one({"nome": body.nome, "id": {"$ne": id}}):
        raise HTTPException(409, "Já existe outro fornecedor com este nome")
    
    doc = body.model_dump()
    await db.fornecedores.update_one({"id": id}, {"$set": doc})
    doc["id"] = id
    return doc

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    em_uso = await db.manutencoes.find_one({"fornecedor_id": id})
    if em_uso:
        raise HTTPException(400, "Não é possível excluir: fornecedor em uso.")
    await db.fornecedores.delete_one({"id": id})
    return {"ok": True}

import httpx

@router.get("/consultar-cnpj/{cnpj}")
async def consultar_cnpj(cnpj: str, _u: dict = Depends(require("read"))):
    cnpj_limpo = "".join(filter(str.isdigit, cnpj))
    if len(cnpj_limpo) != 14:
        raise HTTPException(400, "CNPJ inválido")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}", timeout=10.0)
            if response.status_code != 200:
                raise HTTPException(response.status_code, "Erro ao consultar CNPJ")
            return response.json()
    except httpx.RequestError:
        raise HTTPException(502, "Erro de conexão com a BrasilAPI")
