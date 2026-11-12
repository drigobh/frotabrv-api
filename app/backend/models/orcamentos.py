from pydantic import BaseModel
from typing import List, Optional

class ItemOrcamento(BaseModel):
    produto: str
    quantidade: float
    valor_unitario: float

class OrcamentoCreate(BaseModel):
    fornecedor_id: Optional[str] = None
    fornecedor_nome_ia: Optional[str] = None
    itens: List[ItemOrcamento]
    observacoes: Optional[str] = ""
    origem: str = "Manual" # Manual ou IA
