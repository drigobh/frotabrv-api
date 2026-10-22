from typing import Literal

from pydantic import BaseModel, Field


class MetaIn(BaseModel):
    meta_km_l: float = Field(gt=0, le=20)


class RankingItem(BaseModel):
    posicao: int
    motorista_id: str
    motorista_nome: str
    abastecimentos: int
    litros: float
    km_rodados: float
    media_km_l: float
    percentual_meta: float  # média / meta * 100
    atingiu_meta: bool


class Ranking(BaseModel):
    mes: str  # YYYY-MM
    meta_km_l: float
    media_frota: float | None = None
    itens: list[RankingItem]


class ParabensEnvio(BaseModel):
    mes: str
    enviado_em: str
    origem: Literal["agendado", "manual"]
    motorista_email: str | None = None
    destinatarios: list[str]
    enviados: int
    falhas: list[str]


class CampeaoMes(BaseModel):
    mes: str
    motorista_id: str
    motorista_nome: str
    media_km_l: float
    km_rodados: float
    meta_km_l: float
    atingiu_meta: bool
    participantes: int
    vice_nome: str | None = None
    vice_media: float | None = None
    parabens: ParabensEnvio | None = None


class PlacarItem(BaseModel):
    motorista_id: str
    motorista_nome: str
    vitorias: int
    meses: list[str]
    melhor_media: float


class HistoricoCampeoes(BaseModel):
    meses: list[CampeaoMes]  # mais recente primeiro (só meses fechados)
    placar: list[PlacarItem]  # mais vitórias primeiro
