from pydantic import BaseModel, Field
from typing import Optional

class FornecedorCreate(BaseModel):
    nome: str = Field(min_length=2)
    cnpj: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None
    ativo: bool = True

class Fornecedor(FornecedorCreate):
    id: str
