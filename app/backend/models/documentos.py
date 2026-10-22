from typing import Literal

from pydantic import BaseModel, Field

EntidadeDoc = Literal["veiculo", "motorista"]
SituacaoDoc = Literal["vigente", "vencendo", "vencido"]
_DATA = r"^\d{4}-\d{2}-\d{2}$"


class DocumentoCreate(BaseModel):
    entidade: EntidadeDoc
    entidade_id: str
    tipo: str = Field(min_length=2)  # CRLV, ANTT, Seguro, Tacógrafo, MOPP, Toxicológico…
    numero: str = ""
    emissao: str | None = Field(default=None, pattern=_DATA)
    validade: str = Field(pattern=_DATA)
    observacoes: str = ""


class Documento(DocumentoCreate):
    id: str
    entidade_label: str
    situacao: SituacaoDoc
    dias_restantes: int
    created_by: str
    created_at: str
