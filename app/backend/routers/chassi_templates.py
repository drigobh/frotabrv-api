import uuid
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.chassi_templates import ChassiTemplateCreate, ChassiTemplate

router = APIRouter(prefix="/chassi-templates", tags=["Chassi Templates"])


@router.get("", response_model=list[ChassiTemplate])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.chassi_templates.find({}, {"_id": 0}).sort("nome", 1).to_list(200)
    return [ChassiTemplate(**d) for d in docs]


@router.post("", response_model=ChassiTemplate, status_code=201)
async def criar(body: ChassiTemplateCreate, user: dict = Depends(require("write"))):
    existente = await db.chassi_templates.find_one(
        {"nome": {"$regex": f"^{body.nome}$", "$options": "i"}}
    )
    if existente:
        raise HTTPException(409, "Ja existe um template com este nome.")
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    await db.chassi_templates.insert_one(dict(doc))
    return ChassiTemplate(**doc)


# ROTA FIXA ANTES DAS ROTAS COM PARAMETRO
@router.post("/seed")
async def seed_templates(_u: dict = Depends(require("write"))):
    templates = [
        {"nome": "Cavalo 4x2 Toco", "categoria": "CAVALO", "qtd_estepes": 1, "eixos": [
            {"numero_eixo": 1, "tipo_rodagem": "SIMPLES", "funcao_mecanica": "DIRECIONAL", "tem_suspensor": False},
            {"numero_eixo": 2, "tipo_rodagem": "DUPLA", "funcao_mecanica": "TRACAO", "tem_suspensor": False},
        ]},
        {"nome": "Cavalo 6x2 Trucado Standard", "categoria": "CAVALO", "qtd_estepes": 1, "eixos": [
            {"numero_eixo": 1, "tipo_rodagem": "SIMPLES", "funcao_mecanica": "DIRECIONAL", "tem_suspensor": False},
            {"numero_eixo": 2, "tipo_rodagem": "DUPLA", "funcao_mecanica": "TRACAO", "tem_suspensor": False},
            {"numero_eixo": 3, "tipo_rodagem": "DUPLA", "funcao_mecanica": "TRUCK", "tem_suspensor": True},
        ]},
        {"nome": "Cavalo 6x4 Tracado Pesado", "categoria": "CAVALO", "qtd_estepes": 0, "eixos": [
            {"numero_eixo": 1, "tipo_rodagem": "SIMPLES", "funcao_mecanica": "DIRECIONAL", "tem_suspensor": False},
            {"numero_eixo": 2, "tipo_rodagem": "DUPLA", "funcao_mecanica": "TRACAO", "tem_suspensor": False},
            {"numero_eixo": 3, "tipo_rodagem": "DUPLA", "funcao_mecanica": "TRACAO", "tem_suspensor": False},
        ]},
        {"nome": "Carreta 2 Eixos", "categoria": "CARRETA", "qtd_estepes": 2, "eixos": [
            {"numero_eixo": 1, "tipo_rodagem": "DUPLA", "funcao_mecanica": "LIVRE", "tem_suspensor": True},
            {"numero_eixo": 2, "tipo_rodagem": "DUPLA", "funcao_mecanica": "LIVRE", "tem_suspensor": False},
        ]},
        {"nome": "Carreta 3 Eixos Convencional", "categoria": "CARRETA", "qtd_estepes": 2, "eixos": [
            {"numero_eixo": 1, "tipo_rodagem": "DUPLA", "funcao_mecanica": "LIVRE", "tem_suspensor": True},
            {"numero_eixo": 2, "tipo_rodagem": "DUPLA", "funcao_mecanica": "LIVRE", "tem_suspensor": False},
            {"numero_eixo": 3, "tipo_rodagem": "DUPLA", "funcao_mecanica": "LIVRE", "tem_suspensor": False},
        ]},
        {"nome": "Carreta 3 Eixos Vanderleia", "categoria": "CARRETA", "qtd_estepes": 2, "eixos": [
            {"numero_eixo": 1, "tipo_rodagem": "SIMPLES", "funcao_mecanica": "LIVRE", "tem_suspensor": True},
            {"numero_eixo": 2, "tipo_rodagem": "DUPLA", "funcao_mecanica": "LIVRE", "tem_suspensor": False},
            {"numero_eixo": 3, "tipo_rodagem": "DUPLA", "funcao_mecanica": "LIVRE", "tem_suspensor": False},
        ]},
    ]
    inseridos = 0
    for t in templates:
        existente = await db.chassi_templates.find_one(
            {"nome": {"$regex": f"^{t['nome']}$", "$options": "i"}}
        )
        if not existente:
            t["id"] = str(uuid.uuid4())
            t["created_at"] = now_iso()
            await db.chassi_templates.insert_one(dict(t))
            inseridos += 1
    return {"ok": True, "inseridos": inseridos}


# GET POR ID (DEPOIS das rotas fixas)
@router.get("/{template_id}")
async def obter_template(template_id: str, _u: dict = Depends(require("read"))):
    doc = await db.chassi_templates.find_one({"id": template_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Template de chassi nao encontrado.")
    return doc


@router.put("/{template_id}", response_model=ChassiTemplate)
async def atualizar(template_id: str, body: ChassiTemplateCreate, user: dict = Depends(require("write"))):
    await db.chassi_templates.update_one({"id": template_id}, {"$set": body.model_dump()})
    doc = await db.chassi_templates.find_one({"id": template_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Template nao encontrado.")
    return ChassiTemplate(**doc)


@router.delete("/{template_id}")
async def excluir(template_id: str, _u: dict = Depends(require("delete"))):
    await db.chassi_templates.delete_one({"id": template_id})
    return {"ok": True}
