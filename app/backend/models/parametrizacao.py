from pydantic import BaseModel

class ParametrizacaoBase(BaseModel):
    meta_abastecimento_ativo: bool = False
    meta_abastecimento_valor: float = 2.5
    mostrar_seed_fornecedores: bool = False
    mostrar_seed_medidas: bool = False
    mostrar_seed_marcas: bool = False
    mostrar_seed_modelos: bool = False
    mostrar_seed_templates: bool = False
    mostrar_importacao_pneus: bool = False