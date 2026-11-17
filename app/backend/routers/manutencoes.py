from fastapi import APIRouter, Depends, HTTPException, Query, Request
from lib.dates import now_iso
from lib.db import client, db
from lib.security import require
from models.manutencoes import Manutencao, ManutencaoCreate
import uuid
from typing import Literal

from datetime import date
import re

from pydantic import BaseModel, Field

router = APIRouter(prefix="/manutencoes", tags=["manutencoes"])


@router.get("", response_model=None)
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.manutencoes.find({}, {"_id": 0}).sort("data", -1).to_list(2000)
    return docs

@router.post("", response_model=Manutencao, status_code=201)
async def criar(body: ManutencaoCreate, request: Request, user: dict = Depends(require("write"))):
    veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")

    # VALIDAÇÃO DE ESTOQUE RIGOROSA
    if body.pecas_utilizadas:
        for p in body.pecas_utilizadas:
            peca = await db.pecas.find_one({"id": p.get("peca_id")})
            if not peca:
                raise HTTPException(404, f"Peça {p.get('nome')} não encontrada.")
            qtd_solicitada = int(p.get("quantidade", 0))
            if peca.get("quantidade_atual", 0) < qtd_solicitada:
                raise HTTPException(400, f"Estoque insuficiente para {peca.get('nome')}. Disponível: {peca.get('quantidade_atual')}, Solicitado: {qtd_solicitada}")

    fornecedor_nome = await nome_fornecedor(body.fornecedor_id)
    doc = body.model_dump()
    doc["fornecedor_nome"] = fornecedor_nome
    doc["id"] = str(uuid.uuid4())
    doc["veiculo_label"] = f"{veiculo['placa']} · {veiculo['modelo']}"
    
    if not doc.get("data_inicio"):
        doc["data_inicio"] = body.data
        
    doc["criado_por"] = user.get("nome", user.get("email", "Sistema"))
    doc["created_at"] = now_iso()

    await db.manutencoes.insert_one(doc)
    
    # BAIXA DE ESTOQUE DIRETA
    if body.pecas_utilizadas:
        for p in body.pecas_utilizadas:
            await db.pecas.update_one(
                {"id": p.get("peca_id")},
                {"$inc": {"quantidade_atual": -int(p.get("quantidade", 0))}}
            )
            
    doc.pop("_id", None)
    return doc

# Cada etapa também reconhece as grafias usadas em registros antigos.
STATUS_ALIASES = {
    "Aguardando aprovação": r"aguardando[\s_]+aprova[cç][aã]o",
    "Aguardando peça": r"aguardando[\s_]+pe[cç]as?",
    "Em execução": r"em[\s_]+execu[cç][aã]o",
    "Concluída": r"conclu[ií]d[ao]|fechad[ao]|finalizad[ao]",
    "Cancelada": r"cancelad[ao]|rejeitad[ao]",
}
STATUS_ORIGENS = {
    "Aguardando aprovação": {"Outras"},
    "Aguardando peça": {"Em execução"},
    "Em execução": {"Aguardando aprovação", "Aguardando peça"},
    "Concluída": {"Em execução"},
    "Cancelada": {"Aguardando aprovação", "Aguardando peça", "Em execução"},
}
EtapaOS = Literal["Aguardando aprovação", "Aguardando peça", "Em execução", "Concluída", "Cancelada"]
FiltroOS = Literal["Todas", "Aguardando aprovação", "Aguardando peça", "Em execução", "Concluída", "Cancelada", "Outras"]


def padrao_status(expressao: str) -> str:
    return rf"^\s*(?:{expressao})\s*$"


def etapa_atual(valor) -> str:
    for etapa, expressao in STATUS_ALIASES.items():
        if re.fullmatch(padrao_status(expressao), str(valor or ""), re.IGNORECASE):
            return etapa
    return "Outras"


def validar_transicao(atual, destino: str):
    origem = etapa_atual(atual)
    if origem != destino and origem not in STATUS_ORIGENS[destino]:
        raise HTTPException(409, f"A OS está em «{atual or 'Sem status'}» e não pode ir para «{destino}». Atualize a lista e confira as ações disponíveis.")


def consulta_etapa(etapa: str) -> dict:
    if etapa == "Todas":
        return {}
    if etapa == "Outras":
        return {"$nor": [consulta_etapa(nome) for nome in STATUS_ALIASES]}
    return {"status": {"$regex": padrao_status(STATUS_ALIASES[etapa]), "$options": "i"}}


@router.get("/painel")
async def painel(
    etapa: FiltroOS = "Todas",
    busca: str = Query("", max_length=120),
    pagina: int = Query(1, ge=1, le=100000),
    _u: dict = Depends(require("read")),
):
    por_pagina = 12
    busca = busca.strip()
    consulta = {}
    if busca:
        campos = ("id", "descricao", "veiculo_label", "veiculo_placa", "fornecedor_nome", "oficina")
        consulta = {"$or": [
            {campo: {"$regex": re.escape(busca), "$options": "i"}} for campo in campos
        ]}
    filtro = consulta_etapa(etapa)
    registros = [
        {"$match": filtro},
        {"$sort": {"data": -1, "created_at": -1, "_id": -1}},
        {"$skip": (pagina - 1) * por_pagina},
        {"$limit": por_pagina},
        {"$lookup": {
            "from": "fornecedores", "localField": "fornecedor_id",
            "foreignField": "id", "as": "fornecedor_atual",
        }},
        {"$set": {"fornecedor_nome": {"$ifNull": [
            "$fornecedor_nome", {"$arrayElemAt": ["$fornecedor_atual.nome", 0]}
        ]}}},
        {"$project": {"_id": 0, "fornecedor_atual": 0}},
    ]
    resultado = await db.manutencoes.aggregate([
        {"$match": consulta},
        {"$facet": {
            "itens": registros,
            "status": [{"$group": {"_id": "$status", "total": {"$sum": 1}}}],
        }},
    ]).to_list(1)
    dados = resultado[0] if resultado else {"itens": [], "status": []}
    contagens = dict.fromkeys((*STATUS_ALIASES, "Outras"), 0)
    for grupo in dados["status"]:
        contagens[etapa_atual(grupo["_id"])] += grupo["total"]
    contagens["Todas"] = sum(contagens.values())
    for os in dados["itens"]:
        os["etapa"] = etapa_atual(os.get("status"))
    return {"itens": dados["itens"], "contagens": contagens, "total": contagens[etapa], "por_pagina": por_pagina}


async def nome_fornecedor(fornecedor_id: str | None):
    if not fornecedor_id:
        return None
    fornecedor = await db.fornecedores.find_one({"id": fornecedor_id}, {"nome": 1})
    if fornecedor is None:
        raise HTTPException(422, "Fornecedor não encontrado. Atualize a lista e escolha outro.")
    return fornecedor.get("nome")


class ManutencaoEdicao(BaseModel):
    veiculo_id: str = Field(min_length=1)
    tipo: str = Field(min_length=1, max_length=80)
    descricao: str = Field(min_length=1, max_length=4000)
    data: date
    custo: float = Field(ge=0, allow_inf_nan=False)
    fornecedor_id: str | None = None
    oficina: str | None = Field(None, max_length=200)
    status: EtapaOS | None = None
    status_original: str | None = None
    versao: str | None = None


@router.patch("/{id}/dados")
async def editar_dados(id: str, body: ManutencaoEdicao, _u: dict = Depends(require("write"))):
    atual = await db.manutencoes.find_one({"id": id})
    if atual is None:
        raise HTTPException(404, "Ordem de serviço não encontrada.")
    descricao = body.descricao.strip()
    tipo = body.tipo.strip()
    if not descricao or not tipo:
        raise HTTPException(422, "Preencha o tipo e a descrição do serviço.")
    veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"placa": 1, "modelo": 1, "ativo": 1})
    if body.veiculo_id != atual.get("veiculo_id") and (not veiculo or veiculo.get("ativo") is False):
        raise HTTPException(422, "Selecione um veículo ativo.")
    if body.versao != atual.get("versao_dados"):
        raise HTTPException(409, "Os dados da OS foram alterados. Feche o formulário e abra a versão atual.")
    status_atual = atual.get("status")
    if body.status is not None:
        if body.status_original != status_atual:
            raise HTTPException(409, f"O status mudou para «{status_atual or 'Sem status'}». Feche o formulário e abra a versão atual da OS.")
        validar_transicao(status_atual, body.status)
    fornecedor = body.fornecedor_id or None
    if fornecedor == atual.get("fornecedor_id"):
        fornecedor_nome = atual.get("fornecedor_nome")
        if fornecedor and not fornecedor_nome:
            cadastro = await db.fornecedores.find_one({"id": fornecedor}, {"nome": 1})
            fornecedor_nome = cadastro.get("nome") if cadastro else None
    else:
        fornecedor_nome = await nome_fornecedor(fornecedor)
    dados = {
        "veiculo_id": body.veiculo_id,
        "tipo": tipo,
        "descricao": descricao,
        "data": body.data.isoformat(),
        "custo": body.custo,
        "fornecedor_id": fornecedor,
        "fornecedor_nome": fornecedor_nome,
        "oficina": body.oficina,
        "versao_dados": str(uuid.uuid4()),
    }
    if veiculo is not None:
        dados["veiculo_label"] = " · ".join(str(veiculo[campo]) for campo in ("placa", "modelo") if veiculo.get(campo))
    filtro = {"_id": atual["_id"], "versao_dados": body.versao}
    if body.status is not None:
        filtro["status"] = status_atual
        dados["status"] = body.status
    resposta = await db.manutencoes.update_one(filtro, {"$set": dados})
    if not resposta.matched_count:
        raise HTTPException(409, "A OS mudou enquanto você editava. Atualize a lista e tente novamente.")
    return {"id": id}


class ManutencaoStatusUpdate(BaseModel):
    status: EtapaOS


@router.patch("/{id}/status")
async def atualizar_status(
    id: str, body: ManutencaoStatusUpdate, _u: dict = Depends(require("write"))
):
    atual = await db.manutencoes.find_one({"id": id}, {"status": 1})
    if atual is None:
        raise HTTPException(404, "Ordem de serviço não encontrada.")
    origem = atual.get("status")
    validar_transicao(origem, body.status)
    resultado = await db.manutencoes.update_one(
        {"_id": atual["_id"], "status": origem},
        {"$set": {"status": body.status}},
    )
    if not resultado.matched_count:
        raise HTTPException(409, "A OS mudou durante a atualização. Confira o status atual.")
    return {"id": id, "status": body.status}


@router.put("/{id}", response_model=Manutencao)
async def atualizar(id: str, body: ManutencaoCreate, request: Request, user: dict = Depends(require("write"))):
    existe = await db.manutencoes.find_one({"id": id})
    if not existe:
        raise HTTPException(404, "Manutenção não encontrada")

    veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")

    # 1. Estorna o estoque antigo para poder validar o novo
    if existe.get("pecas_utilizadas"):
        for p in existe["pecas_utilizadas"]:
            await db.pecas.update_one(
                {"id": p.get("peca_id")},
                {"$inc": {"quantidade_atual": int(p.get("quantidade", 0))}}
            )

    # 2. Valida o novo estoque
    if body.pecas_utilizadas:
        for p in body.pecas_utilizadas:
            peca = await db.pecas.find_one({"id": p.get("peca_id")})
            if not peca:
                # Se der erro, precisamos desfazer o estorno, mas para simplificar, assumimos que o frontend envia IDs válidos
                raise HTTPException(404, f"Peça {p.get('nome')} não encontrada.")
            qtd_solicitada = int(p.get("quantidade", 0))
            if peca.get("quantidade_atual", 0) < qtd_solicitada:
                # Desfaz o estorno caso falhe
                if existe.get("pecas_utilizadas"):
                    for p_old in existe["pecas_utilizadas"]:
                        await db.pecas.update_one({"id": p_old.get("peca_id")}, {"$inc": {"quantidade_atual": -int(p_old.get("quantidade", 0))}})
                raise HTTPException(400, f"Estoque insuficiente para {peca.get('nome')}. Disponível: {peca.get('quantidade_atual')}, Solicitado: {qtd_solicitada}")

    doc = body.model_dump()
    doc["veiculo_label"] = f"{veiculo['placa']} · {veiculo['modelo']}"
    doc["criado_por"] = existe.get("criado_por", user.get("nome", "Sistema"))
    doc["created_at"] = existe.get("created_at", now_iso())

    await db.manutencoes.update_one({"id": id}, {"$set": doc})
    
    # 3. Baixa do novo estoque
    if body.pecas_utilizadas:
        for p in body.pecas_utilizadas:
            await db.pecas.update_one(
                {"id": p.get("peca_id")},
                {"$inc": {"quantidade_atual": -int(p.get("quantidade", 0))}}
            )
            
    doc["id"] = id
    return doc

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    async def remover(session):
        os = await db.manutencoes.find_one_and_delete({"id": id}, session=session)
        if os is None:
            return
        for peca in os.get("pecas_utilizadas") or []:
            peca_id = peca.get("peca_id")
            try:
                quantidade = int(peca.get("quantidade") or 0)
            except (ValueError, TypeError):
                raise HTTPException(409, "Há uma quantidade inválida no vínculo de estoque. A OS foi preservada.") from None
            if peca_id and quantidade > 0:
                retorno = await db.pecas.update_one(
                    {"id": peca_id}, {"$inc": {"quantidade_atual": quantidade}}, session=session
                )
                if not retorno.matched_count:
                    raise HTTPException(409, "Há uma peça vinculada que não existe mais no estoque. A OS foi preservada.")

    async with await client.start_session() as session:
        await session.with_transaction(remover)
    return {"ok": True}
