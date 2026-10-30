from pydantic import BaseModel
from typing import Optional

class PneuMovimentacaoCreate(BaseModel):
    pneu_id: str
    tipo: str  # "RODIZIO", "RECAPAGEM", "CONSERTO", "DESCARTE", "APLICACAO"
    veiculo_id: Optional[str] = None
    carreta_id: Optional[str] = None
    posicao_origem: Optional[str] = None
    posicao_destino: Optional[str] = None
    km_veiculo: Optional[float] = None
    motivo: Optional[str] = None
    observacoes: Optional[str] = None
    foto_url: Optional[str] = None

class PneuMovimentacao(PneuMovimentacaoCreate):
    id: str
    created_at: str
    created_by: str
