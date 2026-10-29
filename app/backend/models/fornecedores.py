from pydantic import BaseModel, Field
from typing import Optional

class FornecedorCreate(BaseModel):
    tipo_fornecedor_id: str | None = None | None = None
    tipo_pessoa: str = "PJ" # PJ ou PF
    nome: str = Field(min_length=2)
    documento: Optional[str] = None # CNPJ ou CPF
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    atividade: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    avaliacao: Optional[int] = 0 # 0 a 5
    ativo: bool = True

class Fornecedor(FornecedorCreate):
    id: str
