from pydantic import BaseModel, Field
from typing import Optional

class ManutencaoCreate(BaseModel):
    veiculo_id: str
    tipo: str
    status: str
    descricao: str
    data: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    custo: float = 0.0
    oficina: Optional[str] = None
    fornecedor_id: Optional[str] = None
    km_manutencao: Optional[float] = None
    proxima_revisao_km: Optional[float] = None
    pecas_substituidas: Optional[str] = None
    pecas_utilizadas: Optional[list[dict]] = None

class Manutencao(ManutencaoCreate):
    id: str
    veiculo_label: str
    criado_por: str
    created_at: str
