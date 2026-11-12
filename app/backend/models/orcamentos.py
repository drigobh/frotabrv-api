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
    parcelas: Optional[str] = "1x"
    origem: str = "Manual"
    is_vencedor: bool = False
    classificacao: Optional[float] = 0.0
    compras_realizadas: Optional[int] = 0

class OrcamentoCreate(BaseModel):
    produto: str
    observacoes: Optional[str] = ""
    ofertas: List[Oferta]
