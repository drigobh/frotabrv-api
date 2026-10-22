"""Autenticação (JWT em cookie httpOnly) e autorização por perfil (RBAC).

Uma única função de decisão: `require(acao)`. Perfis:
  admin    -> tudo
  operador -> leitura e escrita (sem excluir, sem gerenciar usuários/auditoria)
"""

import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request

from lib.db import db

COOKIE_NAME = "frota_session"
TOKEN_TTL_HOURS = 12
_ALG = "HS256"

PERMISSOES: dict[str, set[str]] = {
    "admin": {"read", "write", "delete", "admin"},
    "operador": {"read", "write"},
}


def hash_password(senha: str) -> str:
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


def verify_password(senha: str, senha_hash: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode(), senha_hash.encode())
    except ValueError:
        return False


def create_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": user_id, "iat": now, "exp": now + timedelta(hours=TOKEN_TTL_HOURS)}
    return jwt.encode(payload, os.environ["JWT_SECRET"], algorithm=_ALG)


async def current_user(request: Request) -> dict:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    try:
        payload = jwt.decode(token, os.environ["JWT_SECRET"], algorithms=[_ALG])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Sessão expirada")
    # Re-lê o usuário a cada request: perfil/inativação valem imediatamente.
    user = await db.usuarios.find_one({"id": payload.get("sub")}, {"_id": 0})
    if not user or not user.get("ativo"):
        raise HTTPException(status_code=401, detail="Usuário inválido ou inativo")
    return user


def require(acao: str):
    async def dep(user: dict = Depends(current_user)) -> dict:
        if acao not in PERMISSOES.get(user.get("perfil", ""), set()):
            raise HTTPException(status_code=403, detail="Seu perfil não tem permissão para esta ação")
        return user

    return dep
