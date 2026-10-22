from typing import Literal

from pydantic import BaseModel, EmailStr, Field

Perfil = Literal["admin", "operador"]


class Usuario(BaseModel):
    id: str
    nome: str
    email: str
    perfil: Perfil
    ativo: bool
    totp_enabled: bool = False
    created_at: str


class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=2)
    email: EmailStr
    senha: str = Field(min_length=8)
    perfil: Perfil = "operador"


class UsuarioUpdate(BaseModel):
    nome: str = Field(min_length=2)
    perfil: Perfil
    ativo: bool


class SenhaReset(BaseModel):
    senha: str = Field(min_length=8)
