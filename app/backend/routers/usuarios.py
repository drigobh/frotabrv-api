from fastapi import APIRouter, Depends, HTTPException
from lib.db import db

router = APIRouter()

@router.get("")
async def listar_usuarios():
    usuarios = await db.usuarios.find({}, {"_id": 0, "senha": 0}).to_list(1000)
    return usuarios

@router.get("/{id}")
async def obter_usuario(id: str):
    usuario = await db.usuarios.find_one({"id": id}, {"_id": 0, "senha": 0})
    if not usuario:
        raise HTTPException(404, "Usuário não encontrado.")
    return usuario

@router.patch("/{id}/status")
async def alterar_status(id: str, body: dict):
    ativo = body.get("ativo", True)
    await db.usuarios.update_one({"id": id}, {"$set": {"ativo": ativo}})
    return {"status": "ok"}


@router.post("")
async def criar_usuario(body: dict, _u: dict = Depends(require("write"))):
    import uuid
    import bcrypt
    senha_hash = bcrypt.hashpw(body.get("senha", "").encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    novo = {
        "id": str(uuid.uuid4()),
        "nome": body.get("nome"),
        "email": body.get("email"),
        "perfil": body.get("perfil", "Operador"),
        "senha": senha_hash,
        "ativo": True
    }
    await db.usuarios.insert_one(novo)
    novo.pop("_id", None)
    novo.pop("senha", None)
    return novo

@router.put("/{id}")
async def atualizar_usuario(id: str, body: dict, _u: dict = Depends(require("write"))):
    update = {"nome": body.get("nome"), "email": body.get("email"), "perfil": body.get("perfil")}
    await db.usuarios.update_one({"id": id}, {"$set": update})
    return {"status": "ok"}
