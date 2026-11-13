from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import uuid
from services.whatsapp_service import configurado, verificar_status, enviar_mensagem
from lib.db import db
from .auth import require

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

@router.get("/status")
async def status_whatsapp(_u: dict = Depends(require("read"))):
    return verificar_status()

@router.post("/testar")
async def testar_envio(payload: dict, _u: dict = Depends(require("write"))):
    telefone = payload.get("telefone", "")
    mensagem = "Teste Bravus Frota\n\nEsta e uma mensagem de teste. Se voce recebeu, a integracao esta funcionando!"
    resultado = enviar_mensagem(telefone, mensagem)
    # Salvar log no banco
    try:
        await db.whatsapp_logs.insert_one({
            "id": str(uuid.uuid4()),
            "telefone": telefone,
            "mensagem": mensagem,
            "sucesso": resultado.get("sucesso", False),
            "data": datetime.now().isoformat()
        })
    except Exception:
        pass
    return resultado

@router.get("/logs")
async def listar_logs(_u: dict = Depends(require("read"))):
    return await db.whatsapp_logs.find({}, {"_id": 0}).sort("data", -1).to_list(200)
