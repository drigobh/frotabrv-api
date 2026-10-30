from pydantic import BaseModel
from typing import Optional

class PneuCreate(BaseModel):
    numero_fogo: str
    marca: str
    modelo: Optional[str] = None
    medida: str  # Ex: 295/80 R22.5
    dot: Optional[str] = None  # Ex: 4523 (semana 45 de 2023)
    tipo: str = "Tração"  # Direcional, Tração, Misto
    status: str = "Estoque"  # Estoque, Aplicado, Recapagem, Sucateado, Conserto
    custo_aquisicao: float = 0.0
    foto_url: Optional[str] = None
    observacoes: Optional[str] = None

class Pneu(PneuCreate):
    id: str
    created_at: str
    created_by: str
