from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from lib.security import require
from lib.db import db
from lib.security import verify_password, create_token, current_user, COOKIE_NAME, TOKEN_TTL_HOURS
from models.auth import LoginIn, LoginOut

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginOut)
async def login(body: LoginIn, response: Response):
    # Busca o usuário pelo email
    user = await db.usuarios.find_one({"email": body.email.lower().strip()})
    if not user or not verify_password(body.senha, user.get("senha_hash", "")):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    
    if not user.get("ativo"):
        raise HTTPException(status_code=403, detail="Usuário inativo")

    # (Opcional: Aqui entraria a lógica de 2FA se o usuário tiver totp_enabled)

    # Cria o token JWT e salva no cookie httpOnly
    token = create_token(user["id"])
    response.set_cookie(
        key=COOKIE_NAME, 
        value=token, 
        httponly=True, 
        max_age=TOKEN_TTL_HOURS * 3600,
        samesite="none",
        secure=True # Como estamos no Render (HTTPS), deve ser True
    )
    return LoginOut(requires_2fa=False, user=user, token=token)

@router.get("/me")
async def me(_u: dict = Depends(require("read"))):
    usuario = await db.usuarios.find_one({"id": _u["id"]}, {"_id": 0, "senha": 0})
    if not usuario:
        raise HTTPException(404, "Usuário não encontrado.")
    
    # Busca as permissões do perfil
    if usuario.get("perfil_id"):
        perfil = await db.perfis.find_one({"id": usuario["perfil_id"]}, {"_id": 0})
        if perfil:
            usuario["permissoes"] = perfil.get("permissoes", [])
            usuario["perfil_nome"] = perfil.get("nome", "")
    
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
    
    if "nova_senha" in body and body["nova_senha"]:
        import bcrypt
        senha_hash = bcrypt.hashpw(body["nova_senha"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        update_data["senha"] = senha_hash
    
    if update_data:
        await db.usuarios.update_one({"id": _u["id"]}, {"$set": update_data})
    
    return {"status": "ok", "message": "Perfil atualizado!"}

@router.get("/usuarios")
async def listar_usuarios(_u: dict = Depends(require("read"))):
    usuarios = await db.usuarios.find({}, {"_id": 0, "senha": 0}).to_list(1000)
    return usuarios


