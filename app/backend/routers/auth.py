import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from lib.security import USER_RESPONSE_FIELDS, USER_RESPONSE_PROJECTION, hash_user_password, require, user_role
from lib.db import db
from lib.security import verify_password, create_token, current_user, COOKIE_NAME, TOKEN_TTL_HOURS
from models.auth import LoginIn, LoginOut

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginOut)
async def login(body: LoginIn, response: Response):
    # Busca o usuário pelo email
    user = await db.usuarios.find_one({"email": body.email.lower().strip()})
    if not user or not verify_password(body.senha, user.get("senha_hash", user.get("senha"))):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    
    if not user.get("ativo"):
        raise HTTPException(status_code=403, detail="Usuário inativo")

    # (Opcional: Aqui entraria a lógica de 2FA se o usuário tiver totp_enabled)

    login_user = {
        **{campo: user[campo] for campo in USER_RESPONSE_FIELDS if campo in user},
        "perfil": user_role(user),
        "created_at": user.get("created_at") or user.get("data_cadastro") or "",
    }
    token = create_token(user["id"])
    result = LoginOut(requires_2fa=False, user=login_user, token=token)
    response.set_cookie(
        key=COOKIE_NAME, 
        value=token, 
        httponly=True, 
        max_age=TOKEN_TTL_HOURS * 3600,
        samesite="none",
        secure=True # Como estamos no Render (HTTPS), deve ser True
    )
    return result

@router.get("/me")
async def me(_u: dict = Depends(require("read"))):
    usuario = await db.usuarios.find_one({"id": _u["id"]}, USER_RESPONSE_PROJECTION)
    if not usuario:
        raise HTTPException(404, "Usuário não encontrado.")
    
    timeout = 30
    if usuario.get("perfil_id"):
        perfil = await db.perfis.find_one({"id": usuario["perfil_id"]}, {"_id": 0})
        if perfil:
            usuario["permissoes"] = perfil.get("permissoes", [])
            usuario["perfil_nome"] = perfil.get("nome", "")
            timeout = perfil.get("timeout_minutos", 30)
    
    usuario["perfil"] = user_role(usuario)
    usuario["timeout_minutos"] = timeout
    return usuario

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return {"ok": True}
@router.get("/logout")
async def logout_get(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"ok": True, "msg": "Sessão encerrada."}


@router.put("/perfil")
async def atualizar_perfil(body: dict, _u: dict = Depends(require("read"))):
    update_data = {}
    for campo in ["nome", "telefone", "setor", "cargo", "whatsapp", "foto_url", "notificacoes"]:
        if campo in body:
            update_data[campo] = body[campo]
    
    if body.get("nova_senha"):
        update_data["senha_hash"] = hash_user_password(body["nova_senha"])

    if update_data:
        update = {"$set": update_data}
        if "senha_hash" in update_data:
            update["$unset"] = {"senha": ""}
        await db.usuarios.update_one({"id": _u["id"]}, update)
    
    return {"status": "ok", "message": "Perfil atualizado!"}

@router.get("/usuarios")
async def listar_usuarios(_u: dict = Depends(require("read"))):
    usuarios = await db.usuarios.find({"excluido_em": {"$exists": False}}, USER_RESPONSE_PROJECTION).to_list(1000)
    return usuarios



@router.post("/logoff")
async def logoff(_u: dict = Depends(require("read"))):
    from datetime import datetime
    await db.usuarios.update_one({"id": _u["id"]}, {"$set": {"ultimo_logoff": datetime.now().isoformat()}})
    return {"status": "ok"}
