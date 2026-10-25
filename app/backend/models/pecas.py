from pydantic import BaseModel, Field
from typing import Optional

class PecaCreate(BaseModel):
    nome: str = Field(min_length=2)
    codigo: Optional[str] = None
    preco_custo: float = 0.0
    quantidade_estoque: int = 0
    estoque_minimo: int = 5
    fornecedor_id: Optional[str] = None
    ativo: bool = True

class Peca(PecaCreate):
    id: str
    created_by_name: Optional[str] = None
    created_at: Optional[str] = None
