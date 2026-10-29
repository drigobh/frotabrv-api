import uuid
import httpx
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.empresa import EmpresaBase, Empresa

router = APIRouter(prefix="/empresa", tags=["Empresa"])

@router.get("", response_model=list[Empresa])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.empresa.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return [Empresa(**d) for d in docs]

@router.post("", response_model=Empresa, status_code=201)
async def criar(body: EmpresaBase, user: dict = Depends(require("write"))):
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    doc["updated_at"] = now_iso()
    await db.empresa.insert_one(dict(doc))
    return Empresa(**doc)

@router.put("/{id}", response_model=Empresa)
async def atualizar(id: str, body: EmpresaBase, user: dict = Depends(require("write"))):
    doc = body.model_dump()
    doc["updated_at"] = now_iso()
    
    existente = await db.empresa.find_one({"id": id})
    if not existente:
        raise HTTPException(404, "Empresa não encontrada")
        
    await db.empresa.update_one({"id": id}, {"$set": doc})
    doc["id"] = id
    doc["created_at"] = existente["created_at"]
    return Empresa(**doc)

@router.delete("/{id}")
async def excluir(id: str, user: dict = Depends(require("delete"))):
    await db.empresa.delete_one({"id": id})
    return {"ok": True}

@router.get("/cnpj/{cnpj}")
async def buscar_cnpj(cnpj: str, _u: dict = Depends(require("read"))):
    cnpj_limpo = "".join(filter(str.isdigit, cnpj))
    if len(cnpj_limpo) != 14:
        raise HTTPException(400, "CNPJ inválido")
    
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}", timeout=10)
            if res.status_code == 404:
                raise HTTPException(404, "CNPJ não encontrado na base da Receita.")
            res.raise_for_status()
            return res.json()
        except httpx.HTTPError as e:
            raise HTTPException(500, f"Erro ao consultar CNPJ: {str(e)}")

import httpx

@router.get("/geocode")
async def geocode(endereco: str, _u: dict = Depends(require("read"))):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(
                f"https://nominatim.openstreetmap.org/search?format=json&q={endereco}",
                headers={"User-Agent": "FrotaBrv/1.0 (contato@frotabrv.com)"},
                timeout=10
            )
            res.raise_for_status()
            data = res.json()
            if data and len(data) > 0:
                return {"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"])}
            return {"error": "Endereço não encontrado"}
        except Exception as e:
            raise HTTPException(500, f"Erro ao geocodificar: {str(e)}")
