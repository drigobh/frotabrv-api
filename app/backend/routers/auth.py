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
async def me(user: dict = Depends(current_user)):
    # Retorna os dados do usuário logado
    return user

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
    # Atualiza nome e telefone
    update_data = {}
    if "nome" in body: update_data["nome"] = body["nome"]
    if "telefone" in body: update_data["telefone"] = body["telefone"]
    
    if update_data:
        await db.usuarios.update_one({"id": _u["id"]}, {"$set": update_data})
    
    # Atualiza senha (se fornecida)
    if body.get("nova_senha"):
        import bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(body["nova_senha"].encode('utf-8'), salt)
        await db.usuarios.update_one(
            {"id": _u["id"]}, 
            {"$set": {"senha": hashed.decode('utf-8')}}
        )
    
    return {"status": "ok", "message": "Perfil atualizado com sucesso!"}


@router.get("/usuarios")
async def listar_usuarios(_u: dict = Depends(require("read"))):
    usuarios = await db.usuarios.find({}, {"_id": 0, "senha": 0}).to_list(1000)
    return usuarios
