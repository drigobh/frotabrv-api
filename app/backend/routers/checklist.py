from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import uuid
import smtplib
from email.mime.text import MIMEText
from models.checklist import ChecklistViagemCreate, EmailRequest
from lib.db import db
from .auth import require

router = APIRouter(prefix="/checklist", tags=["Checklist"])

def gerar_numero_checklist():
    # Simula um contador. Em produção, usar uma coleção específica para contadores.
    import random
    return f"CHK-{random.randint(1000, 9999)}"

@router.post("")
async def criar_checklist(payload: ChecklistViagemCreate, _u: dict = Depends(require("write"))):
    try:
        # Calcula o risco
        tem_falha = any(i.status == "Falha" for i in payload.itens)
        risco = "Alto" if tem_falha else "Baixo"
        
        doc = {
            "id": str(uuid.uuid4()),
            "numero": gerar_numero_checklist(),
            "veiculo_id": payload.veiculo_id,
            "motorista_id": payload.motorista_id,
            "itens": [item.model_dump() for item in payload.itens],
            "observacoes_gerais": payload.observacoes_gerais,
            "status_geral": payload.status_geral,
            "risco": risco,
            "data_criacao": datetime.now().isoformat(),
            "criado_por": _u.get("nome", "Sistema")
        }
        await db.checklists.insert_one(doc)
        doc.pop("_id", None)
        return doc
    except Exception as e:
        raise HTTPException(400, f"Erro ao salvar checklist: {str(e)}")

@router.get("")
async def listar_checklists(
    veiculo_id: str = None, motorista_id: str = None, data: str = None, _u: dict = Depends(require("read"))
):
    filtro = {}
    if veiculo_id: filtro["veiculo_id"] = veiculo_id
    if motorista_id: filtro["motorista_id"] = motorista_id
    if data: filtro["data_criacao"] = {"$regex": f"^{data}"}
    
    return await db.checklists.find(filtro, {"_id": 0}).sort("data_criacao", -1).to_list(1000)

@router.delete("/{id}")
async def excluir_checklist(id: str, _u: dict = Depends(require("write"))):
    await db.checklists.delete_one({"id": id})
    return {"ok": True}

@router.post("/{id}/email")
async def enviar_email(id: str, payload: EmailRequest, _u: dict = Depends(require("read"))):
    # Simulação de envio de e-mail (em produção, usar variáveis de ambiente para SMTP)
    print(f"Simulando envio de e-mail para {payload.email_destino} sobre o checklist {id}")
    return {"ok": True, "mensagem": "E-mail enviado com sucesso!"}
