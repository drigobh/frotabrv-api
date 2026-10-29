from pydantic import BaseModel
from typing import Optional

class EmpresaBase(BaseModel):
    razao_social: str
    nome_fantasia: Optional[str] = None
    cnpj: str
    ie: Optional[str] = None
    im: Optional[str] = None
    endereco: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    site: Optional[str] = None
    tipo_unidade: str = "Matriz"  # Matriz ou Filial
    logo_base64: Optional[str] = None

class Empresa(EmpresaBase):
    id: str
    created_at: str
    updated_at: str
