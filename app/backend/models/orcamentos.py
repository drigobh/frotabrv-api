from pydantic import BaseModel
from typing import List, Optional

class Oferta(BaseModel):
    fornecedor_id: Optional[str] = None
    fornecedor_nome: str
    whatsapp: Optional[str] = ""
    email: Optional[str] = ""
    quantidade: float
    valor_unitario: float
    prazo_entrega: str
    prazo_pagamento: str
    forma_pagamento: str
    origem: str = "Manual" # Manual ou IA
    is_vencedor: bool = False

class OrcamentoCreate(BaseModel):
    produto: str
    observacoes: Optional[str] = ""
    ofertas: List[Oferta]
