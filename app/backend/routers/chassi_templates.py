import re
import uuid
from lib.chassi_vinculos import categoria_chassi, destino_categoria, transacao_chassi
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.chassi_templates import ChassiTemplateCreate, ChassiTemplate

router = APIRouter(prefix="/chassi-templates", tags=["Chassi Templates"])


@router.get("", response_model=list[ChassiTemplate])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.chassi_templates.find({}, {"_id": 0}).sort("nome", 1).to_list(200)
    destinos = {tipo["_id"]: tipo["destino"] async for tipo in db.chassi_tipos_aplicacao.find()}
    categorias = {c["_id"]: destinos.get(c["familia"]) async for c in db.chassi_categorias.find()}
    return [ChassiTemplate(**{**d, "familia": categorias.get(d["categoria"])}) for d in docs]


@router.post("", response_model=ChassiTemplate, status_code=201)
async def criar(body: ChassiTemplateCreate, user: dict = Depends(require("write"))):
    doc = {**body.model_dump(), "id": str(uuid.uuid4()), "created_at": now_iso()}

    async def inserir(session):
        categoria = await categoria_chassi(body.categoria, session)
        if not categoria or not categoria["ativo"]:
            raise HTTPException(409, "Selecione uma categoria de chassi ativa.")
        existente = await db.chassi_templates.find_one(
            {"nome": {"$regex": f"^{re.escape(body.nome)}$", "$options": "i"}}, session=session
        )
        if existente:
            raise HTTPException(409, "Já existe um template com este nome.")
        await db.chassi_templates.insert_one(dict(doc), session=session)
        return ChassiTemplate(**doc, familia=await destino_categoria(categoria, session))

    return await transacao_chassi(inserir)


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
    async def popular(session):
        inseridos = 0
        for t in templates:
            categoria = await categoria_chassi(t["categoria"], session)
            if not categoria or not categoria["ativo"]:
                continue
            existente = await db.chassi_templates.find_one(
                {"nome": {"$regex": f"^{re.escape(t['nome'])}$", "$options": "i"}}, session=session
            )
            if not existente:
                doc = {**t, "id": str(uuid.uuid4()), "created_at": now_iso()}
                await db.chassi_templates.insert_one(doc, session=session)
                inseridos += 1
        return {"ok": True, "inseridos": inseridos}

    return await transacao_chassi(popular)


# GET POR ID (DEPOIS das rotas fixas)
@router.get("/{template_id}")
async def obter_template(template_id: str, _u: dict = Depends(require("read"))):
    doc = await db.chassi_templates.find_one({"id": template_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Template de chassi nao encontrado.")
    return doc


@router.put("/{template_id}", response_model=ChassiTemplate)
async def atualizar(template_id: str, body: ChassiTemplateCreate, user: dict = Depends(require("write"))):
    async def editar(session):
        filtro = {"id": template_id}
        doc = await db.chassi_templates.find_one(filtro, {"_id": 0}, session=session)
        if not doc:
            raise HTTPException(404, "Template não encontrado.")
        categoria = await categoria_chassi(body.categoria, session)
        if body.categoria != doc["categoria"]:
            if not categoria or not categoria["ativo"]:
                raise HTTPException(409, "Selecione uma categoria de chassi ativa.")
            await verificar_template_em_uso(template_id, session)
        dados = body.model_dump()
        await db.chassi_templates.update_one(filtro, {"$set": dados}, session=session)
        return ChassiTemplate(**{**doc, **dados, "familia": await destino_categoria(categoria, session)})

    return await transacao_chassi(editar)


async def verificar_template_em_uso(template_id: str, session):
    filtro = {"template_chassi_id": template_id}
    for colecao in (db.veiculos, db.carretas):
        if await colecao.find_one(filtro, {"_id": 1}, session=session):
            raise HTTPException(409, "Template aplicado a um veículo ou carreta. Remova o vínculo primeiro.")


@router.delete("/{template_id}")
async def excluir(template_id: str, _u: dict = Depends(require("delete"))):
    async def remover(session):
        await verificar_template_em_uso(template_id, session)
        resultado = await db.chassi_templates.delete_one({"id": template_id}, session=session)
        if not resultado.deleted_count:
            raise HTTPException(404, "Template não encontrado.")
    await transacao_chassi(remover)
    return {"ok": True}
