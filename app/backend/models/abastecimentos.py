from typing import Literal
from pydantic import BaseModel, Field

class AbastecimentoCreate(BaseModel):
    data: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    veiculo_id: str
    motorista_id: str | None = None
    combustivel_id: str | None = None
    produto: str | None = None
    litros: float = Field(gt=0)
    preco_litro: float = Field(gt=0)
    posto: str | None = None
    km: float = Field(ge=0)
    observacoes: str = ""
    numero_nf: str | None = None
    chave_nfe: str | None = None
    hora: str | None = None
    cnpj: str | None = None
    cidade: str | None = None
    estado: str | None = None
    fornecedor: str | None = None
    origem: str = "manual"

class Abastecimento(AbastecimentoCreate):
    id: str
    valor_total: float
    km_rodados: float | None = None
    media_km_l: float | None = None
    veiculo_label: str
    motorista_label: str | None = None
    created_by: str
    created_at: str
