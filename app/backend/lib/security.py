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

COOKIE_NAME = "frota_session_v2"
TOKEN_TTL_HOURS = 12
_ALG = "HS256"

# Allowlist dos campos de cadastro presentes nas respostas de usuários.
USER_RESPONSE_FIELDS = (
    "id", "nome", "email", "perfil", "perfil_id", "ativo", "cargo",
    "setor", "telefone", "whatsapp", "foto_url", "data_cadastro",
    "created_at", "ultimo_acesso", "notificacoes", "limite_aprovacao",
    "limite_compra", "pode_aprovar_compras", "pode_comprar",
    "totp_enabled", "two_factor_enabled",
)
USER_RESPONSE_PROJECTION = {"_id": 0, **dict.fromkeys(USER_RESPONSE_FIELDS, 1)}

PERMISSOES: dict[str, set[str]] = {
    "admin": {"read", "write", "delete", "admin"},
    "operador": {"read", "write"},
}


def hash_password(senha: str) -> str:
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


def hash_user_password(senha: str) -> str:
    if not isinstance(senha, str) or len(senha) < 6 or len(senha.encode()) > 72:
        raise HTTPException(400, "A senha precisa ter no mínimo 6 caracteres e no máximo 72 bytes.")
    return hash_password(senha)


def verify_password(senha: str, senha_hash: str) -> bool:
    if not isinstance(senha_hash, str):
        return False
    try:
        return bcrypt.checkpw(senha.encode(), senha_hash.encode())
    except ValueError:
        return False


def user_role(user: dict) -> str:
    return user.get("perfil", "operador")


def create_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": user_id, "iat": now, "exp": now + timedelta(hours=TOKEN_TTL_HOURS)}
    return jwt.encode(payload, os.environ["JWT_SECRET"], algorithm=_ALG)


async def current_user(request: Request) -> dict:
    authorization = request.headers.get("Authorization", "")
    scheme, _, credentials = authorization.partition(" ")
    token = (
        credentials.strip()
        if scheme.lower() == "bearer"
        else request.cookies.get(COOKIE_NAME)
    )
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
        if acao not in PERMISSOES.get(user_role(user), set()):
            raise HTTPException(status_code=403, detail="Seu perfil não tem permissão para esta ação")
        return user

    return dep
