import uuid
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.tipos_fornecedores import TipoFornecedorCreate, TipoFornecedor

router = APIRouter(prefix="/tipos-fornecedores", tags=["Tipos de Fornecedores"])

@router.get("", response_model=list[TipoFornecedor])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.tipos_fornecedores.find({}, {"_id": 0}).sort("nome", 1).to_list(1000)
    return [TipoFornecedor(**d) for d in docs]

@router.post("", response_model=TipoFornecedor, status_code=201)
async def criar(body: TipoFornecedorCreate, user: dict = Depends(require("write"))):
    # Verifica se já existe na mesma categoria
    existente = await db.tipos_fornecedores.find_one({
        "nome": {"$regex": f"^{body.nome}$", "$options": "i"},
        "categoria_pai_id": body.categoria_pai_id
    })
    if existente:
        raise HTTPException(409, "Já existe um tipo com este nome nesta categoria.")
    
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    await db.tipos_fornecedores.insert_one(dict(doc))
    return TipoFornecedor(**doc)

@router.put("/{id}", response_model=TipoFornecedor)
async def atualizar(id: str, body: TipoFornecedorCreate, user: dict = Depends(require("write"))):
    await db.tipos_fornecedores.update_one({"id": id}, {"$set": body.model_dump()})
    doc = await db.tipos_fornecedores.find_one({"id": id}, {"_id": 0})
    return TipoFornecedor(**doc)

@router.delete("/{id}")
async def excluir(id: str, user: dict = Depends(require("delete"))):
    # Verifica se tem sub-itens
    sub = await db.tipos_fornecedores.find_one({"categoria_pai_id": id})
    if sub:
        raise HTTPException(400, "Não é possível excluir uma categoria que possui sub-itens.")
    await db.tipos_fornecedores.delete_one({"id": id})
    return {"ok": True}
