from pydantic import BaseModel
from typing import Optional

class TipoFornecedorCreate(BaseModel):
    nome: str
    categoria_pai_id: Optional[str] = None

class TipoFornecedor(TipoFornecedorCreate):
    id: str
    created_at: str
