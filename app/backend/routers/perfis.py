from fastapi import APIRouter, Depends, HTTPException
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
        "timeout_minutos": int(body.get("timeout_minutos", 30)),
        "tentativas_login": str(body.get("tentativas_login", "5"))
    }
    await db.perfis.insert_one(novo)
    novo.pop("_id", None)
    return novo

@router.put("/{id}")
async def atualizar_perfil(id: str, body: dict, _u: dict = Depends(require("write"))):
    update = {
        "nome": body.get("nome"),
        "descricao": body.get("descricao", ""),
        "permissoes": body.get("permissoes", []),
        "timeout_minutos": int(body.get("timeout_minutos", 30)),
        "tentativas_login": str(body.get("tentativas_login", "5"))
    }
    await db.perfis.update_one({"id": id}, {"$set": update})
    return {"status": "ok"}

@router.delete("/{id}")
async def excluir_perfil(id: str, _u: dict = Depends(require("write"))):
    await db.perfis.delete_one({"id": id})
    return {"status": "ok"}


@router.post("/migrar-seguranca")
async def migrar_seguranca():
    """Força todos os perfis a terem os campos de segurança."""
    perfis = await db.perfis.find({}).to_list(100)
    for p in perfis:
        update = {}
        if "timeout_minutos" not in p or p.get("timeout_minutos") is None:
            update["timeout_minutos"] = 30
        if "tentativas_login" not in p or p.get("tentativas_login") is None:
            update["tentativas_login"] = "5"
        
        if update:
            await db.perfis.update_one({"id": p["id"]}, {"$set": update})
    
    return {"status": "ok", "message": "Perfis migrados com sucesso."}

