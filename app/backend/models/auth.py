from pydantic import BaseModel, Field

from models.usuarios import Usuario


class LoginIn(BaseModel):
    email: str
    senha: str
    codigo: str | None = None


class LoginOut(BaseModel):
    token: str | None = None
    requires_2fa: bool
    user: Usuario | None = None


class TwoFASetupOut(BaseModel):
    secret: str
    otpauth_url: str
    qr_code: str  # data URL (PNG base64)


class CodigoIn(BaseModel):
    codigo: str = Field(min_length=6, max_length=6)


class TrocaSenhaIn(BaseModel):
    senha_atual: str
    nova_senha: str = Field(min_length=8)


class OkOut(BaseModel):
    ok: bool = True
