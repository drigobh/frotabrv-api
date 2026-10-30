from pydantic import BaseModel
from typing import Optional

class PneuMedidaCreate(BaseModel):
    codigo: str  # Ex: 295/80 R22.5
    aro: str
    tipo_construcao: str = "RADIAL"
    requer_camara: bool = False

class PneuMedida(PneuMedidaCreate):
    id: str
    created_at: str
