from pydantic import BaseModel, Field
from typing import Optional

class FornecedorCreate(BaseModel):
    tipo_pessoa: str = "PJ"
    nome: str = Field(min_length=2)
    documento: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    atividade: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    avaliacao: Optional[int] = 0
    contrato_inicio: Optional[str] = None
    contrato_fim: Optional[str] = None
    ativo: bool = True

class Fornecedor(FornecedorCreate):
    id: str
