import re

from pydantic import BaseModel, Field, field_validator


class VeiculoCreate(BaseModel):
    placa: str = Field(min_length=7, max_length=8)
    modelo: str = Field(min_length=1)
    ano: int = Field(ge=1950, le=2100)
    hodometro_km: float = Field(default=0, ge=0)
    observacoes: str = ""

    @field_validator("placa", mode="before")
    @classmethod
    def _placa(cls, v: str) -> str:
        return str(v).upper().replace("-", "").strip()


class Veiculo(VeiculoCreate):
    id: str
    ativo: bool
    acoplado: bool = False
    created_at: str


class CarretaCreate(BaseModel):
    codigo: str = Field(min_length=1)
    tipo: str = Field(min_length=1)
    observacoes: str = ""

    @field_validator("codigo", mode="before")
    @classmethod
    def _codigo(cls, v: str) -> str:
        return str(v).upper().strip()


class Carreta(CarretaCreate):
    id: str
    ativo: bool
    acoplado: bool = False
    created_at: str


class MotoristaCreate(BaseModel):
    nome: str = Field(min_length=2)
    cnh: str = Field(min_length=5)
    categoria_cnh: str = "E"
    validade_cnh: str | None = None  # YYYY-MM-DD
    telefone: str = ""
    email: str = ""  # opcional — recebe o parabéns quando for campeão do mês
    observacoes: str = ""

    @field_validator("email", mode="before")
    @classmethod
    def _email(cls, v: str | None) -> str:
        v = (v or "").strip().lower()
        if v and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", v):
            raise ValueError("E-mail inválido")
        return v
    @classmethod
    def _cnh(cls, v: str) -> str:
        return str(v).strip()

    @field_validator("validade_cnh", mode="before")
    @classmethod
    def _validade(cls, v: str | None) -> str | None:
        return v or None


class Motorista(MotoristaCreate):
    id: str
    ativo: bool
    acoplado: bool = False
    created_at: str
