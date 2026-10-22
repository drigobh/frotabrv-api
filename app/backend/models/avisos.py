from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class AvisoItem(BaseModel):
    categoria: Literal["documento", "cnh", "pagar", "receber"]
    titulo: str
    detalhe: str
    data: str  # YYYY-MM-DD (validade/vencimento)
    dias: int  # negativo = vencido
    valor: float | None = None


class AvisoResumo(BaseModel):
    gerado_em: str
    ate: str  # limite da janela (hoje + 30)
    documentos: list[AvisoItem]
    contas_pagar: list[AvisoItem]
    contas_receber: list[AvisoItem]
    total_pagar: float
    total_receber: float


class AvisoConfigIn(BaseModel):
    emails_extras: list[EmailStr] = Field(default_factory=list, max_length=20)


class AvisoConfig(BaseModel):
    emails_extras: list[str]
    admins: list[str]
    destinatarios: list[str]


class AvisoEnvio(BaseModel):
    id: str
    origem: Literal["agendado", "manual"]
    enviado_em: str
    destinatarios: list[str]
    enviados: int
    falhas: list[str]
    itens: int
    usuario: str | None = None
