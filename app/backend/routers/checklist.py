from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import uuid
import smtplib
from email.mime.text import MIMEText
from models.checklist import ChecklistViagemCreate, EmailRequest
from lib.db import db
from .auth import require

router = APIRouter(prefix="/checklist", tags=["Checklist"])

async def gerar_numero_checklist():
    # Usa a coleção de contadores para garantir sequencial único e crescente
    res = await db.contadores.find_one_and_update(
        {"_id": "checklist"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    seq = res.get("seq", 1) if res else 1
    return f"CHK-{seq:05d}"

@router.post("")
async def criar_checklist(payload: ChecklistViagemCreate, _u: dict = Depends(require("write"))):
    try:
        # Calcula o risco
        tem_falha = any(i.status == "Falha" for i in payload.itens)
        risco = "Alto" if tem_falha else "Baixo"
        
        doc = {
            "id": str(uuid.uuid4()),
            "numero": await gerar_numero_checklist(),
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


@router.put("/{id}")
async def editar_checklist(id: str, payload: ChecklistViagemCreate, _u: dict = Depends(require("write"))):
    try:
        # Busca o checklist antigo para comparar
        antigo = await db.checklists.find_one({"id": id})
        if not antigo:
            raise HTTPException(404, "Checklist não encontrado")
            
        tem_falha = any(i.status == "Falha" for i in payload.itens)
        risco = "Alto" if tem_falha else "Baixo"
        
        # Verifica se estava reprovado e agora foi aprovado
        estava_reprovado = antigo.get("status_geral") == "Reprovado"
        esta_aprovado = payload.status_geral == "Aprovado"
        
        # Prepara os dados de atualização
        update_data = {
            "veiculo_id": payload.veiculo_id,
            "motorista_id": payload.motorista_id,
            "itens": [item.model_dump() for item in payload.itens],
            "observacoes_gerais": payload.observacoes_gerais,
            "status_geral": payload.status_geral,
            "risco": risco
        }

        # Se foi corrigido (passou de Reprovado para Aprovado)
        if estava_reprovado and esta_aprovado:
            update_data["aprovado_por"] = _u.get("nome", "Sistema")
            update_data["data_aprovacao"] = datetime.now().isoformat()
            
            # Verifica exatamente quais itens mudaram de Falha para OK/N/A
            itens_corrigidos = []
            for item_novo in payload.itens:
                # Encontra o item correspondente no antigo
                item_antigo = next((i for i in antigo["itens"] if i["nome"] == item_novo.nome and i["categoria"] == item_novo.categoria), None)
                if item_antigo and item_antigo["status"] == "Falha" and item_novo.status != "Falha":
                    itens_corrigidos.append({
                        "item": item_novo.nome,
                        "categoria": item_novo.categoria,
                        "de": "Falha",
                        "para": item_novo.status
                    })

            # Registra o histórico do que foi corrigido, agora com detalhes
            historico_antigo = antigo.get("historico_correcoes", [])
            historico_antigo.append({
                "data": datetime.now().isoformat(),
                "usuario": _u.get("nome", "Sistema"),
                "acao": "Correção e Aprovação",
                "veiculo_id": payload.veiculo_id,
                "motorista_id": payload.motorista_id,
                "itens_corrigidos": itens_corrigidos
            })
            update_data["historico_correcoes"] = historico_antigo

        await db.checklists.update_one({"id": id}, {"$set": update_data})
        return {"ok": True}
    except Exception as e:
        raise HTTPException(400, f"Erro ao editar checklist: {str(e)}")

