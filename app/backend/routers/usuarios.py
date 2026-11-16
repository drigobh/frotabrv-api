from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import DuplicateKeyError
from lib.db import db

router = APIRouter()
from lib.security import USER_RESPONSE_FIELDS, USER_RESPONSE_PROJECTION, hash_user_password, require

@router.get("", dependencies=[Depends(require("admin"))])
async def listar_usuarios():
    usuarios = await db.usuarios.find({"excluido_em": {"$exists": False}}, USER_RESPONSE_PROJECTION).to_list(1000)
    return usuarios

@router.get("/{id}", dependencies=[Depends(require("admin"))])
async def obter_usuario(id: str):
    usuario = await db.usuarios.find_one({"id": id, "excluido_em": {"$exists": False}}, USER_RESPONSE_PROJECTION)
    if not usuario:
        raise HTTPException(404, "Usuário não encontrado.")
    return usuario

@router.patch("/{id}/status", dependencies=[Depends(require("admin"))])
async def alterar_status(id: str, body: dict):
    ativo = body.get("ativo", True)
    resultado = await db.usuarios.update_one(
        {"id": id, "excluido_em": {"$exists": False}}, {"$set": {"ativo": ativo}}
    )
    if not resultado.matched_count:
        raise HTTPException(404, "Usuário não encontrado.")
    return {"status": "ok"}


@router.delete("/{id}", dependencies=[Depends(require("admin"))])
async def excluir_usuario(id: str):
    alvo = {"id": id}
    resultado = await db.usuarios.delete_one(
        {**alvo, "perfil": {"$ne": "admin"}, "perfil_id": {"$ne": "perfil-admin"}},
    )
    if resultado.deleted_count == 0:
        if await db.usuarios.find_one(alvo, {"_id": 1}):
            raise HTTPException(409, "Contas administrativas não podem ser excluídas.")
        raise HTTPException(404, "Usuário não encontrado.")
    return {"status": "ok"}
