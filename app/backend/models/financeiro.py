from typing import Literal

from pydantic import BaseModel, Field

TipoConta = Literal["pagar", "receber"]
OrigemConta = Literal["abastecimento", "manutencao", "frete", "manual"]
StatusConta = Literal["aberta", "paga"]
_DATA = r"^\d{4}-\d{2}-\d{2}$"


class ContaCreate(BaseModel):
    """Lançamento manual (contas automáticas nascem de abastecimentos, manutenções e fretes)."""

    tipo: TipoConta
    descricao: str = Field(min_length=2)
    categoria: str = "Outros"
    veiculo_id: str | None = None
    valor: float = Field(gt=0)
    vencimento: str = Field(pattern=_DATA)


class Conta(BaseModel):
    id: str
    tipo: TipoConta
    origem: OrigemConta
    origem_id: str | None = None
    descricao: str
    categoria: str
    veiculo_id: str | None = None
    veiculo_label: str | None = None
    valor: float
    vencimento: str
    status: StatusConta
    pago_em: str | None = None
    vencida: bool = False
    created_by: str
    created_at: str


class BaixaIn(BaseModel):
    data: str = Field(pattern=_DATA)


class FreteCreate(BaseModel):
    data: str = Field(pattern=_DATA)
    veiculo_id: str
    motorista_id: str | None = None
    cliente: str = Field(min_length=2)
    origem: str = Field(min_length=2)
    destino: str = Field(min_length=2)
    valor: float = Field(gt=0)
    vencimento: str = Field(pattern=_DATA)
    observacoes: str = ""


class Frete(FreteCreate):
    id: str
    veiculo_label: str
    motorista_label: str | None = None
    created_by: str
    created_at: str


class RentabilidadeVeiculo(BaseModel):
    veiculo_id: str
    veiculo_label: str
    viagens: int
    receita: float
    combustivel: float
    manutencao: float
    outras_despesas: float
    lucro: float
    margem: float | None = None  # % sobre receita
    km_rodados: float
    custo_km: float | None = None


class ResumoFinanceiro(BaseModel):
    inicio: str
    fim: str
    receita_total: float
    despesa_total: float
    lucro_total: float
    a_pagar_aberto: float
    a_receber_aberto: float
    vencidas_pagar: int
    vencidas_receber: int
    veiculos: list[RentabilidadeVeiculo]
