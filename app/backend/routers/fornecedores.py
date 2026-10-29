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
    doc["contato"] = getattr(body, "contato", None)
    doc["whatsapp"] = getattr(body, "whatsapp", None)
    doc["contato"] = getattr(body, "contato", None)
    doc["whatsapp"] = getattr(body, "whatsapp", None)
    doc["contato"] = getattr(body, "contato", None)
    doc["whatsapp"] = getattr(body, "whatsapp", None)
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
    doc["contato"] = getattr(body, "contato", None)
    doc["whatsapp"] = getattr(body, "whatsapp", None)
    doc["contato"] = getattr(body, "contato", None)
    doc["whatsapp"] = getattr(body, "whatsapp", None)
    doc["contato"] = getattr(body, "contato", None)
    doc["whatsapp"] = getattr(body, "whatsapp", None)
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

import httpx
from urllib.parse import quote

@router.get("/consultar-cnpj-por-nome")
async def consultar_cnpj_por_nome(nome: str, cidade: str = None, _u: dict = Depends(require("read"))):
    if not nome:
        raise HTTPException(400, "Nome do estabelecimento é obrigatório.")
    
    # Monta a URL de busca do OpenCNPJ
    # A API aceita filtros por nome e município.
    query = f"https://api.opencnpj.org/search?query={quote(nome)}"
    if cidade:
        query += f"&city={quote(cidade)}"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(query)
            if response.status_code == 200:
                data = response.json()
                # A resposta pode vir como lista ou objeto com 'results'
                if isinstance(data, list) and len(data) > 0:
                    return data[0]  # Retorna o primeiro resultado
                elif isinstance(data, dict) and 'results' in data and len(data['results']) > 0:
                    return data['results'][0]
            # Se não encontrar no OpenCNPJ, tenta fallback com BrasilAPI (se tiver CNPJ)
            # Mas como não temos CNPJ, não há fallback direto.
    except Exception as e:
        print(f"Erro na busca reversa: {e}")
    
    raise HTTPException(404, "CNPJ não encontrado para este estabelecimento.")


@router.delete("/limpar")
async def limpar_fornecedores(_u: dict = Depends(require("delete"))):
    await db.fornecedores.delete_many({})
    return {"ok": True}
