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
