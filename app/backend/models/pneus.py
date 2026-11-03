from pydantic import BaseModel
from typing import Optional

class PneuCreate(BaseModel):
    numero_fogo: str
    marca: str
    modelo: Optional[str] = None
    medida: str
    dot: Optional[str] = None
    tipo: str = "Tração"
    status: str = "Estoque"
    custo_aquisicao: float = 0.0
    observacoes: Optional[str] = None
    foto_url: Optional[str] = None
    
    equipamento: Optional[str] = None
    posicao: Optional[str] = None
    banda_rod: Optional[str] = None
    estrutura: Optional[str] = None
    n_serie: Optional[str] = None
    n_recap: Optional[str] = None
    data_compra: Optional[str] = None
    data_descarte: Optional[str] = None
    custo_total_atual: Optional[float] = None
    profundidade_atual: Optional[float] = None
    uso_atual: Optional[str] = None
    custo_por_km: Optional[float] = None
    km_posicao: Optional[float] = None
    
    veiculo_id: Optional[str] = None
    carreta_id: Optional[str] = None

class Pneu(PneuCreate):
    id: str
    created_at: str
    created_by: str
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None
