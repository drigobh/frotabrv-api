from fastapi import APIRouter, Depends, HTTPException, Response, Request
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
        samesite="lax",
        secure=True # Como estamos no Render (HTTPS), deve ser True
    )
    return LoginOut(requires_2fa=False, user=user)

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
