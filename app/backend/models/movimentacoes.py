from pydantic import BaseModel, Field
from typing import Optional, List

class MovimentacaoCreate(BaseModel):
    peca_id: str
    fornecedor_id: Optional[str] = None
    veiculo_id: Optional[str] = None
    carreta_id: Optional[str] = None
    quantidade: int
    motivo: str
    observacao: Optional[str] = None

class Movimentacao(MovimentacaoCreate):
    id: str
    peca_nome: str
    fornecedor_nome: Optional[str] = None
    destino_nome: Optional[str] = None
    usuario_nome: str
    data_hora: str

class InventarioItem(BaseModel):
    peca_id: str
    peca_nome: str
    qtd_anterior: int
    qtd_fisica: int

class InventarioPayload(BaseModel):
    itens: List[InventarioItem]

class Inventario(BaseModel):
    id: str
    data_hora: str
    usuario_nome: str
    total_ajustes: int
    itens: List[InventarioItem]
