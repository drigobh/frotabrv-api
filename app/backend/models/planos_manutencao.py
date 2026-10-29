from pydantic import BaseModel
from typing import Optional

class PlanoManutencaoCreate(BaseModel):
    veiculo_id: str | None = None
    carreta_id: str | None = None
    carreta_id: str | None = None
    familia: str  # Ex: Lubrificação, Transmissão, Segurança
    descricao: str
    tipo_gatilho: str
    tipo_recorrencia: str = "periodico" # "periodico" ou "vitalicio"
    unidade_tempo: str | None = None # "dias", "meses", "anos"
    data_abertura: str  # "km", "horas" ou "dias"
    intervalo: float  # Ex: 20000 (km) ou 180 (dias)
    ultima_execucao_km: Optional[float] = None
    ultima_execucao_data: Optional[str] = None
    ativo: bool = True

class PlanoManutencao(PlanoManutencaoCreate):
    id: str
    veiculo_label: str
    created_by: str
    created_at: str
