from pydantic import BaseModel, Field
from typing import Optional

class CombustivelCreate(BaseModel):
    nome: str = Field(min_length=2)
    is_arla: bool = False
    ativo: bool = True

class Combustivel(CombustivelCreate):
    id: str
