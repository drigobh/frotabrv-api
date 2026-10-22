from pydantic import BaseModel, Field


class AbastecimentoCreate(BaseModel):
    data: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    veiculo_id: str
    motorista_id: str | None = None
    litros: float = Field(gt=0)
    preco_litro: float = Field(gt=0)
    posto: str = Field(min_length=1)
    km: float = Field(ge=0)
    observacoes: str = ""


class Abastecimento(AbastecimentoCreate):
    id: str
    valor_total: float
    km_rodados: float | None = None
    media_km_l: float | None = None
    veiculo_label: str
    motorista_label: str | None = None
    created_by: str
    created_at: str
