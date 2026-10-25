from pydantic import BaseModel, Field
from typing import Optional, List

class FornecedorPreco(BaseModel):
    fornecedor_id: str
    preco_atual: float = 0.0
    historico: List[float] = []

class PecaCreate(BaseModel):
    nome: str = Field(min_length=2)
    codigo: Optional[str] = None
    codigo_barras: Optional[str] = None
    corredor: Optional[str] = None
    prateleira: Optional[str] = None
    caixa: Optional[str] = None
    quantidade_estoque: int = 0
    estoque_minimo: int = 5
    fornecedor_atual_id: Optional[str] = None
    fornecedores_precos: List[FornecedorPreco] = []
    ativo: bool = True

class Peca(PecaCreate):
    id: str
    created_by_name: Optional[str] = None
    created_at: Optional[str] = None
