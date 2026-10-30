from pydantic import BaseModel
from typing import Optional

class ParametrizacaoBase(BaseModel):
    meta_abastecimento_ativo: bool = False
    meta_abastecimento_valor: float = 2.5
    mostrar_seed_fornecedores: bool = False
    mostrar_seed_medidas: bool = False
    mostrar_seed_marcas: bool = False

class Parametrizacao(ParametrizacaoBase):
    id: str
    updated_at: str
