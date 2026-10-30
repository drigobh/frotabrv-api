from pydantic import BaseModel
from typing import Optional

class PneuMarcaCreate(BaseModel):
    nome: str
    tipo: str  # "FABRICANTE_NOVO", "SISTEMA_REFORMA", "AMBOS"
    tier: Optional[str] = None  # "TIER_1", "TIER_2", "TIER_3"

class PneuMarca(PneuMarcaCreate):
    id: str
    created_at: str
