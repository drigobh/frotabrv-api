from pydantic import BaseModel
from typing import Optional

class PlanoManutencaoCreate(BaseModel):
    veiculo_id: Optional[str] = None
    carreta_id: Optional[str] = None
    familia: str
    descricao: str
    tipo_gatilho: str
    tipo_recorrencia: str = "periodico"
    unidade_tempo: Optional[str] = None
    intervalo: float
    ultima_execucao_km: Optional[float] = None
    ultima_execucao_data: Optional[str] = None
    data_abertura: str
    ativo: bool = True

class PlanoManutencao(PlanoManutencaoCreate):
    id: str
    veiculo_label: str
    created_by: str
    created_at: str
