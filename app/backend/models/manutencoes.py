from typing import Literal

from pydantic import BaseModel, Field

TipoManutencao = Literal["preventiva", "corretiva"]
StatusManutencao = Literal["agendada", "em_execucao", "concluida"]


class ManutencaoCreate(BaseModel):
    veiculo_id: str
    tipo: TipoManutencao
    descricao: str = Field(min_length=2)
    oficina: str = ""
    custo: float = Field(default=0, ge=0)
    data: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    km: float | None = None
    pecas: str = ""
    status: StatusManutencao = "agendada"
    proxima_km: float | None = None  # alerta preventivo por KM


class Manutencao(ManutencaoCreate):
    id: str
    veiculo_label: str
    created_by: str
    created_at: str
