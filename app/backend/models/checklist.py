from pydantic import BaseModel
from typing import List, Optional

class ItemChecklist(BaseModel):
    categoria: str
    nome: str
    status: str  # "OK", "Falha", "N/A"
    observacao: Optional[str] = ""

class ChecklistViagemCreate(BaseModel):
    veiculo_id: str
    motorista_id: str
    itens: List[ItemChecklist]
    observacoes_gerais: Optional[str] = ""
    status_geral: str  # "Aprovado", "Reprovado"

class EmailRequest(BaseModel):
    email_destino: str
