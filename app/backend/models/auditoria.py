from pydantic import BaseModel


class AuditoriaItem(BaseModel):
    id: str
    usuario_nome: str
    acao: str
    entidade: str
    entidade_id: str | None = None
    detalhes: str = ""
    ip: str | None = None
    created_at: str
