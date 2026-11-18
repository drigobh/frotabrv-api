import csv
import io
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from lib.dates import now_iso
from lib.db import client, db
from lib.security import require
from models.manutencoes import Manutencao, ManutencaoCreate
import uuid
from typing import Literal

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import math
import re

from pydantic import BaseModel, Field

router = APIRouter(prefix="/manutencoes", tags=["manutencoes"])


def evento_os(acao: str, usuario: dict, alteracoes: list[dict]) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "acao": acao,
        "data": now_iso(),
        "autor": usuario.get("nome") or usuario.get("id") or "Sistema",
        "alteracoes": alteracoes,
    }


def valor_historico(os: dict):
    custo = os.get("custo")
    return os.get("valor") if custo is None else custo


def fornecedor_historico(os: dict):
    return os.get("fornecedor_nome") or os.get("fornecedor_id")


def alteracoes_os(anterior: dict, dados: dict) -> list[dict]:
    atual = {**anterior, **dados}
    comparacoes = [
        ("status", anterior.get("status"), atual.get("status")),
        ("valor", valor_historico(anterior), valor_historico(atual)),
    ]
    if anterior.get("fornecedor_id") != atual.get("fornecedor_id"):
        comparacoes.append(("fornecedor", fornecedor_historico(anterior), fornecedor_historico(atual)))
    return [
        {"campo": campo, "antes": antes, "depois": depois}
        for campo, antes, depois in comparacoes if antes != depois
    ]


def escrita_os(anterior: dict, dados: dict, usuario: dict) -> dict:
    escrita = {"$set": dados}
    alteracoes = alteracoes_os(anterior, dados)
    if alteracoes:
        escrita["$push"] = {"historico_os": evento_os("alteracao", usuario, alteracoes)}
    return escrita


@router.get("/{id}/historico")
async def historico_os(id: str, _u: dict = Depends(require("read"))):
    os = await db.manutencoes.find_one(
        {"id": id}, {"_id": 0, "historico_os": 1, "criado_por": 1, "created_at": 1},
    )
    if os is None:
        raise HTTPException(404, "Ordem de serviço não encontrada.")
    eventos = list(os.get("historico_os") or [])
    abertura_registrada = any(evento.get("acao") == "abertura" for evento in eventos)
    if not abertura_registrada and os.get("created_at"):
        eventos.insert(0, {
            "id": "abertura-original",
            "acao": "abertura",
            "data": os["created_at"],
            "autor": os.get("criado_por") or "Autor não registrado",
            "alteracoes": [],
        })
    return {"eventos": eventos, "anterior_ao_historico": not abertura_registrada}


@router.get("", response_model=None)
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.manutencoes.find({}, {"_id": 0, "historico_os": 0}).sort("data", -1).to_list(2000)
    return docs

async def plano_da_os(plano_id, tipo, veiculo_id, session=None):
    if not plano_id:
        return None
    if str(tipo).strip().casefold() != "preventiva":
        raise HTTPException(422, "Apenas uma OS preventiva pode ter um plano vinculado.")
    plano = await db.planos_manutencao.find_one({"id": plano_id}, session=session)
    if not plano or plano.get("ativo") is False or plano.get("veiculo_id") != veiculo_id:
        raise HTTPException(422, "Selecione um plano ativo do veículo desta OS.")
    if plano.get("tipo_gatilho") not in {"km", "dias"}:
        raise HTTPException(422, "O vínculo está disponível para planos por quilometragem ou calendário.")
    return plano


def dados_execucao_plano(plano: dict, os: dict) -> dict:
    ultima = plano.get("ultima_execucao_data")
    if plano.get("tipo_recorrencia") == "vitalicio" and (
        ultima or plano.get("ultima_execucao_km") is not None
    ):
        raise HTTPException(409, "Este plano vitalício já teve uma execução registrada.")
    data_execucao = hoje_manutencao().isoformat()
    if ultima and ultima[:10] > data_execucao:
        raise HTTPException(409, "O plano tem uma execução com data posterior à conclusão.")
    dados = {"ultima_execucao_data": data_execucao, "ultima_execucao_os_id": os["id"]}
    if plano["tipo_gatilho"] == "km":
        km = os.get("km_manutencao")
        if not isinstance(km, (int, float)) or not math.isfinite(km) or km < 0:
            raise HTTPException(422, "Informe o hodômetro da execução antes de concluir a OS.")
        ultima_km = plano.get("ultima_execucao_km")
        if ultima_km is not None and km < ultima_km:
            raise HTTPException(409, "O hodômetro da execução é menor que o último registrado no plano.")
        dados["ultima_execucao_km"] = km
    return dados


async def atualizar_os_com_plano(anterior, filtro, dados, user, session=None):
    atual = {**anterior, **dados}
    plano_id = atual.get("plano_manutencao_id")
    plano_anterior_id = anterior.get("plano_manutencao_id")
    estava_concluida = etapa_atual(anterior.get("status")) == "Concluída"
    vai_concluir = not estava_concluida and etapa_atual(atual.get("status")) == "Concluída"
    campos_vinculo = ("plano_manutencao_id", "veiculo_id", "tipo", "km_manutencao")
    mudou_vinculo = any(atual.get(campo) != anterior.get(campo) for campo in campos_vinculo)
    if estava_concluida and (plano_id or plano_anterior_id) and (
        mudou_vinculo or etapa_atual(atual.get("status")) != "Concluída"
    ):
        raise HTTPException(409, "O vínculo e o hodômetro de uma OS preventiva concluída não podem ser alterados.")

    if mudou_vinculo and (plano_id or plano_anterior_id):
        filtro = {**filtro, "status": anterior.get("status")}

    async def salvar(sessao):
        plano = None
        if plano_id and (mudou_vinculo or vai_concluir):
            plano = await plano_da_os(plano_id, atual.get("tipo"), atual.get("veiculo_id"), sessao)
        execucao = dados_execucao_plano(plano, atual) if plano and vai_concluir else None
        resposta = await db.manutencoes.update_one(
            filtro, escrita_os(anterior, dados, user), session=sessao,
        )
        if resposta.matched_count and execucao:
            await db.planos_manutencao.update_one({"_id": plano["_id"]}, {"$set": execucao}, session=sessao)
        return resposta

    if session is not None or not (plano_id and vai_concluir):
        return await salvar(session)
    async with await client.start_session() as sessao:
        return await sessao.with_transaction(salvar)


@router.post("", response_model=Manutencao, status_code=201)
async def criar(body: ManutencaoCreate, request: Request, user: dict = Depends(require("write"))):
    veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")

    quantidades = {}
    for item in body.pecas_utilizadas or []:
        peca_id = item.get("peca_id")
        quantidade = item.get("quantidade")
        if not isinstance(peca_id, str) or not peca_id.strip():
            raise HTTPException(422, "Informe o identificador da peça.")
        try:
            unidades = int(quantidade)
        except (TypeError, ValueError, OverflowError):
            raise HTTPException(422, "Informe uma quantidade inteira e positiva.") from None
        if isinstance(quantidade, bool) or unidades <= 0 or (
            not isinstance(quantidade, str) and unidades != quantidade
        ):
            raise HTTPException(422, "Informe uma quantidade inteira e positiva.")
        quantidades[peca_id] = quantidades.get(peca_id, 0) + unidades

    if body.plano_manutencao_id:
        await plano_da_os(body.plano_manutencao_id, body.tipo, body.veiculo_id)
        if etapa_atual(body.status) != "Aguardando aprovação":
            raise HTTPException(422, "Abra a OS vinculada em Aguardando aprovação.")
    fornecedor_nome = await nome_fornecedor(body.fornecedor_id)
    doc = body.model_dump()
    doc["fornecedor_nome"] = fornecedor_nome
    doc["id"] = str(uuid.uuid4())
    doc["veiculo_label"] = f"{veiculo['placa']} · {veiculo['modelo']}"
    
    if not doc.get("data_inicio"):
        doc["data_inicio"] = body.data
        
    doc["criado_por"] = user.get("nome", user.get("email", "Sistema"))
    doc["created_at"] = now_iso()

    abertura = [
        {"campo": "status", "antes": None, "depois": doc.get("status")},
        {"campo": "valor", "antes": None, "depois": valor_historico(doc)},
    ]
    if doc.get("fornecedor_id"):
        abertura.append({"campo": "fornecedor", "antes": None, "depois": fornecedor_historico(doc)})
    doc["historico_os"] = [evento_os("abertura", user, abertura)]
    if not quantidades:
        await db.manutencoes.insert_one(dict(doc))
        return doc

    async def salvar_com_pecas(session):
        for peca_id, unidades in sorted(quantidades.items()):
            resultado = await db.pecas.update_one(
                {"id": peca_id, "quantidade_estoque": {"$gte": unidades}},
                {"$inc": {"quantidade_estoque": -unidades}},
                session=session,
            )
            if resultado.matched_count == 0:
                peca = await db.pecas.find_one({"id": peca_id}, session=session)
                if not peca:
                    raise HTTPException(404, f"Peça {peca_id} não encontrada.")
                disponivel = peca.get("quantidade_estoque", 0)
                raise HTTPException(
                    400,
                    f"Estoque insuficiente para {peca.get('nome', peca_id)}. "
                    f"Disponível: {disponivel}, solicitado: {unidades}.",
                )

        await db.manutencoes.insert_one(dict(doc), session=session)

    async with await client.start_session() as session:
        await session.with_transaction(salvar_com_pecas)
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


def hoje_manutencao() -> date:
    return datetime.now(ZoneInfo("America/Sao_Paulo")).date()


def resumo_painel(filtro: dict) -> list[dict]:
    def para_data(campo):
        return {"$convert": {"input": campo, "to": "date", "onError": None, "onNull": None}}

    inicio = {"$ifNull": [para_data("$data_inicio"), para_data("$data")]}
    fim = {"$ifNull": [
        para_data("$fim_registrado"),
        {"$cond": ["$em_andamento", para_data(hoje_manutencao().isoformat()), None]},
    ]}
    return [
        {"$match": filtro},
        {"$project": {
            "_id": 0,
            "os_id": "$id",
            "veiculo_id": {"$ifNull": ["$veiculo_id", ""]},
            "placa": {"$ifNull": ["$veiculo_placa", ""]},
            "rotulo": {"$ifNull": ["$veiculo_label", ""]},
            "valor": {"$convert": {
                "input": {"$ifNull": ["$custo", "$valor"]},
                "to": "double", "onError": 0, "onNull": 0,
            }},
            "inicio": {"$dateTrunc": {"date": inicio, "unit": "day"}},
            "fim_registrado": "$data_fim",
            "em_andamento": {"$regexMatch": {
                "input": {"$convert": {"input": "$status", "to": "string", "onError": "", "onNull": ""}},
                "regex": padrao_status(
                    STATUS_ALIASES["Em execução"] + "|" + STATUS_ALIASES["Aguardando peça"]
                ),
                "options": "i",
            }},
        }},
        {"$set": {
            "fim": {"$dateTrunc": {"date": fim, "unit": "day"}},
            "nome_veiculo": {"$cond": [{"$ne": ["$rotulo", ""]}, "$rotulo", "$placa"]},
        }},
        {"$set": {
            "dias": {"$cond": [
                {"$and": [{"$ne": ["$inicio", None]}, {"$ne": ["$fim", None]}, {"$gte": ["$fim", "$inicio"]}]},
                {"$dateDiff": {"startDate": "$inicio", "endDate": "$fim", "unit": "day"}},
                None,
            ]},
            "chave_veiculo": {"$cond": [
                {"$ne": ["$veiculo_id", ""]},
                {"tipo": "id", "valor": "$veiculo_id"},
                {"tipo": "rotulo", "valor": "$nome_veiculo"},
            ]},
        }},
    ]


def ranking_veiculos(base: list[dict], ordem: dict) -> list[dict]:
    return [
        *base,
        {"$match": {"chave_veiculo.valor": {"$ne": ""}}},
        {"$group": {
            "_id": "$chave_veiculo", "valor": {"$sum": "$valor"},
            "quantidade": {"$sum": 1}, "nome": {"$max": "$nome_veiculo"},
        }},
        {"$sort": {**ordem, "_id": 1}},
        {"$limit": 1},
        {"$project": {
            "_id": 0,
            "veiculo": {"$cond": [{"$ne": ["$nome", ""]}, "$nome", "$_id.valor"]},
            "valor": 1, "quantidade": 1,
        }},
    ]


def filtro_periodo_painel(de: date | None, ate: date | None) -> dict:
    if de and ate and de > ate:
        raise HTTPException(422, "A data inicial deve ser anterior ou igual à data final.")
    if not de and not ate:
        return {}

    texto = {"$type": "string"}
    data_bson = {"$type": "date"}
    for operador, limite in (
        ("$gte", de),
        ("$lt", ate + timedelta(days=1) if ate and ate != date.max else None),
    ):
        if limite is not None:
            texto[operador] = limite.isoformat()
            data_bson[operador] = datetime.combine(limite, datetime.min.time())
    return {"$or": [{"data": texto}, {"data": data_bson}]}


def consulta_painel(busca: str, de: date | None, ate: date | None) -> dict:
    busca = busca.strip()
    consulta = {}
    if busca:
        campos = ("id", "descricao", "veiculo_label", "veiculo_placa", "fornecedor_nome", "oficina")
        consulta = {"$or": [
            {campo: {"$regex": re.escape(busca), "$options": "i"}} for campo in campos
        ]}
    periodo = filtro_periodo_painel(de, ate)
    if periodo:
        consulta = {"$and": [consulta, periodo]} if consulta else periodo
    return consulta


OrdemPainel = Literal["recentes", "antigas", "maior_valor", "menor_valor"]


def ordenar_painel(ordem: OrdemPainel) -> list[dict]:
    if ordem == "antigas":
        return [{"$sort": {"data": 1, "created_at": 1, "_id": 1}}]

    recentes = {"data": -1, "created_at": -1, "_id": -1}
    if ordem == "recentes":
        return [{"$sort": recentes}]

    direcao = -1 if ordem == "maior_valor" else 1
    return [
        {"$set": {"ordem_painel_valor": {"$convert": {
            "input": {"$ifNull": ["$custo", "$valor"]},
            "to": "decimal", "onError": None, "onNull": None,
        }}}},
        {"$set": {"ordem_painel_sem_valor": {"$eq": ["$ordem_painel_valor", None]}}},
        {"$sort": {"ordem_painel_sem_valor": 1, "ordem_painel_valor": direcao, **recentes}},
        {"$unset": ["ordem_painel_valor", "ordem_painel_sem_valor"]},
    ]

FORNECEDOR_PAINEL = [
        {"$lookup": {
            "from": "fornecedores", "localField": "fornecedor_id",
            "foreignField": "id", "as": "fornecedor_atual",
        }},
        {"$set": {"fornecedor_nome": {"$ifNull": [
            "$fornecedor_nome", {"$arrayElemAt": ["$fornecedor_atual.nome", 0]}
        ]}}},
        {"$project": {"_id": 0, "fornecedor_atual": 0, "historico_os": 0}},
]


def texto_csv(valor) -> str:
    texto = "" if valor is None else str(valor)
    if texto.startswith(("\t", "\n", "\r")) or texto.lstrip().startswith(("=", "+", "-", "@", "＝", "＋", "－", "＠")):
        return "'" + texto
    return texto


def valor_csv(os: dict) -> str:
    valor = os.get("custo")
    if valor is None:
        valor = os.get("valor")
    try:
        numero = Decimal(str(valor))
        return format(numero, ".2f").replace(".", ",") if numero.is_finite() else ""
    except InvalidOperation:
        return ""


async def gerar_csv(cursor):
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, delimiter=";", lineterminator="\r\n")

    def linha(campos):
        buffer.seek(0)
        buffer.truncate()
        writer.writerow(campos)
        return buffer.getvalue()

    try:
        yield "\ufeff" + linha([
            "OS", "Data de abertura", "Veículo", "Descrição", "Tipo",
            "Fornecedor", "Oficina", "Status", "Valor (R$)",
        ])
        async for os in cursor:
            etapa = etapa_atual(os.get("status"))
            status = os.get("status") if etapa == "Outras" else etapa
            campos = [
                os.get("id"), os.get("data"), os.get("veiculo_label") or os.get("veiculo_placa"),
                os.get("descricao"), os.get("tipo"), os.get("fornecedor_nome"),
                os.get("oficina"), status,
            ]
            yield linha([*(texto_csv(campo) for campo in campos), valor_csv(os)])
    finally:
        await cursor.close()


@router.get("/painel/exportar")
async def exportar_painel(
    etapa: FiltroOS = "Todas",
    ordem: OrdemPainel = "recentes",
    busca: str = Query("", max_length=120),
    de: date | None = None,
    ate: date | None = None,
    _u: dict = Depends(require("read")),
):
    cursor = db.manutencoes.aggregate([
        {"$match": consulta_painel(busca, de, ate)},
        {"$match": consulta_etapa(etapa)},
        *ordenar_painel(ordem),
        *FORNECEDOR_PAINEL,
    ], allowDiskUse=True)
    return StreamingResponse(
        gerar_csv(cursor),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="ordens-de-servico.csv"',
            "Cache-Control": "no-store",
        },
    )


@router.get("/painel")
async def painel(
    etapa: FiltroOS = "Todas",
    ordem: OrdemPainel = "recentes",
    busca: str = Query("", max_length=120),
    pagina: int = Query(1, ge=1, le=100000),
    de: date | None = None,
    ate: date | None = None,
    _u: dict = Depends(require("read")),
):
    por_pagina = 12
    consulta = consulta_painel(busca, de, ate)
    filtro = consulta_etapa(etapa)
    registros = [
        {"$match": filtro},
        *ordenar_painel(ordem),
        {"$skip": (pagina - 1) * por_pagina},
        {"$limit": por_pagina},
        *FORNECEDOR_PAINEL,
    ]
    base_resumo = resumo_painel(filtro)
    resultado = await db.manutencoes.aggregate([
        {"$match": consulta},
        {"$facet": {
            "itens": registros,
            "status": [{"$group": {"_id": "$status", "total": {"$sum": 1}}}],
            "valor": [*base_resumo, {"$group": {"_id": None, "total": {"$sum": "$valor"}}}],
            "duracao": [
                *base_resumo,
                {"$match": {"dias": {"$ne": None}}},
                {"$sort": {"dias": -1, "os_id": 1}},
                {"$limit": 1},
                {"$project": {"dias": 1, "os_id": 1, "veiculo": "$nome_veiculo"}},
            ],
            "maior_valor": ranking_veiculos(base_resumo, {"valor": -1, "quantidade": -1}),
            "maior_quantidade": ranking_veiculos(base_resumo, {"quantidade": -1, "valor": -1}),
        }},
    ]).to_list(1)
    dados = resultado[0] if resultado else {"itens": [], "status": []}
    contagens = dict.fromkeys((*STATUS_ALIASES, "Outras"), 0)
    for grupo in dados["status"]:
        contagens[etapa_atual(grupo["_id"])] += grupo["total"]
    contagens["Todas"] = sum(contagens.values())
    for os in dados["itens"]:
        os["etapa"] = etapa_atual(os.get("status"))
    def primeiro(campo: str):
        registros = dados.get(campo, [])
        return registros[0] if registros else None

    return {
        "itens": dados["itens"], "contagens": contagens,
        "total": contagens[etapa], "por_pagina": por_pagina,
        "indicadores": {
            "valor": (primeiro("valor") or {}).get("total", 0),
            "duracao": primeiro("duracao"),
            "maior_valor": primeiro("maior_valor"),
            "maior_quantidade": primeiro("maior_quantidade"),
        },
    }


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
    plano_manutencao_id: str | None = None
    km_manutencao: float | None = Field(None, ge=0, allow_inf_nan=False)


@router.patch("/{id}/dados")
async def editar_dados(id: str, body: ManutencaoEdicao, user: dict = Depends(require("write"))):
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
        if atual.get("fornecedor_id") and not atual.get("fornecedor_nome"):
            anterior = await db.fornecedores.find_one({"id": atual["fornecedor_id"]}, {"nome": 1})
            if anterior:
                atual["fornecedor_nome"] = anterior.get("nome")
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
    for campo in ("plano_manutencao_id", "km_manutencao"):
        if campo in body.model_fields_set:
            dados[campo] = getattr(body, campo)
    if veiculo is not None:
        dados["veiculo_label"] = " · ".join(str(veiculo[campo]) for campo in ("placa", "modelo") if veiculo.get(campo))
    filtro = {"_id": atual["_id"], "versao_dados": body.versao}
    if body.status is not None:
        filtro["status"] = status_atual
        dados["status"] = body.status
        if body.status == "Concluída" and etapa_atual(status_atual) != "Concluída" and not atual.get("data_fim"):
            dados["data_fim"] = hoje_manutencao().isoformat()
    resposta = await atualizar_os_com_plano(atual, filtro, dados, user)
    if not resposta.matched_count:
        raise HTTPException(409, "A OS mudou enquanto você editava. Atualize a lista e tente novamente.")
    return {"id": id}


class ManutencaoStatusUpdate(BaseModel):
    status: EtapaOS


@router.patch("/{id}/status")
async def atualizar_status(
    id: str, body: ManutencaoStatusUpdate, user: dict = Depends(require("write"))
):
    atual = await db.manutencoes.find_one({"id": id})
    if atual is None:
        raise HTTPException(404, "Ordem de serviço não encontrada.")
    origem = atual.get("status")
    validar_transicao(origem, body.status)
    dados = {"status": body.status}
    if body.status == "Concluída" and etapa_atual(origem) != "Concluída" and not atual.get("data_fim"):
        dados["data_fim"] = hoje_manutencao().isoformat()
    resultado = await atualizar_os_com_plano(
        atual, {"_id": atual["_id"], "status": origem, "versao_dados": atual.get("versao_dados")}, dados, user,
    )
    if not resultado.matched_count:
        raise HTTPException(409, "A OS mudou durante a atualização. Confira o status atual.")
    return {"id": id, "status": body.status}


@router.put("/{id}", response_model=Manutencao)
async def atualizar(id: str, body: ManutencaoCreate, request: Request, user: dict = Depends(require("write"))):
    async def salvar(session):
        existe = await db.manutencoes.find_one({"id": id}, session=session)
        if not existe:
            raise HTTPException(404, "Manutenção não encontrada")

        veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0}, session=session)
        if not veiculo:
            raise HTTPException(404, "Veículo não encontrado")

        for peca in existe.get("pecas_utilizadas") or []:
            await db.pecas.update_one(
                {"id": peca.get("peca_id")},
                {"$inc": {"quantidade_estoque": int(peca.get("quantidade", 0))}},
                session=session,
            )

        for item in body.pecas_utilizadas or []:
            quantidade = int(item.get("quantidade", 0))
            peca = await db.pecas.find_one({"id": item.get("peca_id")}, session=session)
            if not peca:
                raise HTTPException(404, f"Peça {item.get('nome')} não encontrada.")
            if peca.get("quantidade_estoque", 0) < quantidade:
                raise HTTPException(400, f"Estoque insuficiente para {peca.get('nome')}.")
            await db.pecas.update_one(
                {"id": item.get("peca_id")}, {"$inc": {"quantidade_estoque": -quantidade}}, session=session,
            )

        doc = body.model_dump()
        if "plano_manutencao_id" not in body.model_fields_set:
            doc.pop("plano_manutencao_id", None)
        if "km_manutencao" not in body.model_fields_set:
            doc.pop("km_manutencao", None)
        if doc.get("fornecedor_id") != existe.get("fornecedor_id"):
            fornecedor = await db.fornecedores.find_one(
                {"id": doc["fornecedor_id"]}, {"nome": 1}, session=session,
            ) if doc.get("fornecedor_id") else None
            doc["fornecedor_nome"] = fornecedor.get("nome") if fornecedor else None
            if existe.get("fornecedor_id") and not existe.get("fornecedor_nome"):
                anterior = await db.fornecedores.find_one(
                    {"id": existe["fornecedor_id"]}, {"nome": 1}, session=session,
                )
                if anterior:
                    existe["fornecedor_nome"] = anterior.get("nome")
        doc["veiculo_label"] = f"{veiculo['placa']} · {veiculo['modelo']}"
        doc["criado_por"] = existe.get("criado_por", user.get("nome", "Sistema"))
        doc["created_at"] = existe.get("created_at", now_iso())
        doc["versao_dados"] = str(uuid.uuid4())
        await atualizar_os_com_plano(existe, {"_id": existe["_id"]}, doc, user, session=session)
        return {**doc, "id": id}

    async with await client.start_session() as session:
        return await session.with_transaction(salvar)


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
                    {"id": peca_id}, {"$inc": {"quantidade_estoque": quantidade}}, session=session
                )
                if not retorno.matched_count:
                    raise HTTPException(409, "Há uma peça vinculada que não existe mais no estoque. A OS foi preservada.")

    async with await client.start_session() as session:
        await session.with_transaction(remover)
    return {"ok": True}
