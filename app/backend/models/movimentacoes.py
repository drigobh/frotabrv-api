from pydantic import BaseModel, Field
from typing import Optional, List

class MovimentacaoCreate(BaseModel):
    peca_id: str
    tipo: str # entrada, saida, ajuste
    quantidade: int
    motivo: str
    observacao: Optional[str] = None

class Movimentacao(MovimentacaoCreate):
    id: str
    peca_nome: str
    usuario_nome: str
    data_hora: str

class InventarioItem(BaseModel):
    peca_id: str
    quantidade_fisica: int

class InventarioPayload(BaseModel):
    itens: List[InventarioItem]
