from typing import Literal

from pydantic import BaseModel

Campo = Literal["veiculo", "carreta", "motorista"]


class AcoplamentoCreate(BaseModel):
    veiculo_id: str
    carreta_id: str | None = None
    motorista_id: str | None = None


class AcoplamentoTroca(BaseModel):
    campo: Campo
    novo_id: str | None = None  # None = desacoplar o item (carreta/motorista)


class Acoplamento(BaseModel):
    id: str
    veiculo_id: str
    veiculo_label: str
    carreta_id: str | None = None
    carreta_label: str | None = None
    motorista_id: str | None = None
    motorista_label: str | None = None
    status: Literal["ativo", "liberado", "excluido"]
    completo: bool
    created_at: str
    created_by: str
    updated_at: str


class HistoricoItem(BaseModel):
    id: str
    acoplamento_id: str
    conjunto: str  # placa do cavalo (identifica o conjunto)
    evento: str  # "Novo Conjunto", "Troca de motorista", "Liberação", ...
    item: Literal["veiculo", "carreta", "motorista", "conjunto"]
    descricao: str
    status: Literal["Acoplado", "Desacoplado", "Excluído"]
    usuario: str
    created_at: str
