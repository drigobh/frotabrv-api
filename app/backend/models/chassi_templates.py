from pydantic import BaseModel
from typing import Optional

class ChassiTemplateEixo(BaseModel):
    numero_eixo: int
    tipo_rodagem: str
    funcao_mecanica: str
    tem_suspensor: bool = False

class ChassiTemplateCreate(BaseModel):
    nome: str
    categoria: str
    qtd_estepes: int = 0
    eixos: list[ChassiTemplateEixo] = []

class ChassiTemplate(ChassiTemplateCreate):
    id: str
    created_at: str
