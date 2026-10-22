from typing import Literal

from pydantic import BaseModel

from models.acoplamentos import HistoricoItem


class SeriePonto(BaseModel):
    mes: str  # YYYY-MM
    valor: float


class Kpi(BaseModel):
    chave: Literal["veiculos", "motoristas", "acoplamentos", "km"]
    titulo: str
    valor: float
    tendencia: float | None = None  # % vs mês anterior
    serie: list[SeriePonto]


class StatusFrota(BaseModel):
    acoplados: int
    disponiveis: int
    em_manutencao: int
    inativos: int


class CustoMes(BaseModel):
    mes: str
    combustivel: float
    manutencao: float


class Alerta(BaseModel):
    tipo: Literal["manutencao", "cnh", "documento"]
    titulo: str
    detalhe: str
    severidade: Literal["alta", "media"]


class Campeao(BaseModel):
    mes: str  # YYYY-MM
    motorista_nome: str
    media_km_l: float
    km_rodados: float
    meta_km_l: float
    atingiu_meta: bool
    participantes: int


class Campeoes(BaseModel):
    mes_passado: Campeao | None = None
    mes_atual: Campeao | None = None


class Dashboard(BaseModel):
    kpis: list[Kpi]
    status_frota: StatusFrota
    custos: list[CustoMes]
    alertas: list[Alerta]
    historico_recente: list[HistoricoItem]
    campeoes: Campeoes
