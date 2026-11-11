from pydantic import BaseModel
from typing import List, Optional

class ItemCompra(BaseModel):
    descricao: str
    quantidade: float
    valor_unitario: float

class PedidoCompraCreate(BaseModel):
    fornecedor_id: str
    veiculo_id: Optional[str] = None
    itens: List[ItemCompra]
    observacoes: Optional[str] = ""
    valor_total: float

class AprovacaoPayload(BaseModel):
    status: str  # "Aprovado" ou "Reprovado"
    motivo: Optional[str] = ""
