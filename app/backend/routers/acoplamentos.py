import uuid
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Request
from lib.audit import audit
from lib.chassi_vinculos import transacao_chassi as transacao_vinculos
from lib.dates import now_iso
from lib.db import db
from lib.security import require
from models.acoplamentos import Acoplamento, AcoplamentoCreate, HistoricoItem

router = APIRouter(prefix="/acoplamentos", tags=["Acoplamentos"])

async def _get_labels(veiculo_id: str, carreta_id: str | None, motorista_id: str | None, session) -> tuple[str, str | None, str | None]:
    veiculo = await db.veiculos.find_one({"id": veiculo_id}, session=session)
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")
    if veiculo.get("ativo") is not True:
        raise HTTPException(409, "Veículo inativo. Reative o cadastro antes de acoplar.")
    v_label = f"{veiculo['placa']} - {veiculo.get('modelo', '')}"
    
    c_label = None
    if carreta_id:
        carreta = await db.carretas.find_one({"id": carreta_id}, session=session)
        if not carreta:
            raise HTTPException(404, "Carreta não encontrada")
        if carreta.get("ativo") is not True:
            raise HTTPException(409, "Carreta inativa. Reative o cadastro antes de acoplar.")
        c_label = f"{carreta['codigo']} - {carreta.get('tipo', '')}"
        
    m_label = None
    if motorista_id:
        motorista = await db.motoristas.find_one({"id": motorista_id}, session=session)
        if not motorista:
            raise HTTPException(404, "Motorista não encontrado")
        if motorista.get("ativo") is not True:
            raise HTTPException(409, "Motorista inativo. Reative o cadastro antes de acoplar.")
        m_label = motorista['nome']

    return v_label, c_label, m_label

ITENS_ACOPLAMENTO = (
    ("veiculo", "Cavalo / veículo"),
    ("carreta", "Carreta"),
    ("motorista", "Motorista"),
)


def evento_historico(atual, usuario, agora, evento, item, descricao, status):
    conjunto = atual.get("veiculo_label") or atual["veiculo_id"]
    return {
        "id": str(uuid.uuid4()),
        "acoplamento_id": atual["id"],
        "conjunto": conjunto.split(" - ", 1)[0],
        "evento": evento,
        "item": item,
        "descricao": descricao,
        "status": status,
        "usuario": usuario,
        "created_at": agora,
    }


async def verificar_disponibilidade(body, session, ignorar_id=None):
    conflitos = []
    for campo, funcao in ITENS_ACOPLAMENTO:
        item_id = getattr(body, f"{campo}_id")
        if not item_id:
            continue
        filtro = {f"{campo}_id": item_id, "status": "ativo"}
        if ignorar_id is not None:
            filtro["id"] = {"$ne": ignorar_id}
        conjunto = await db.acoplamentos.find_one(
            filtro, sort=[("created_at", -1)], session=session
        )
        if conjunto:
            conflitos.append({
                "funcao": funcao,
                "item": conjunto.get(f"{campo}_label") or item_id,
                "conjunto_id": conjunto.get("id"),
                "veiculo": conjunto.get("veiculo_label"),
                "carreta": conjunto.get("carreta_label"),
                "motorista": conjunto.get("motorista_label"),
                "inicio_conjunto": conjunto.get("data_inicio") or conjunto.get("created_at"),
                "vinculado_em": conjunto.get(f"{campo}_vinculado_em"),
            })
    if conflitos:
        raise HTTPException(409, detail={
            "codigo": "ITENS_EM_USO",
            "mensagem": "Os itens abaixo já estão em acoplamentos ativos.",
            "conflitos": conflitos,
        })


@router.get("", response_model=list[Acoplamento])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.acoplamentos.find({"status": "ativo"}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
    # Busca manutenções ativas (qualquer status que não seja finalizado/fechado/cancelado)
    status_encerrado = r"^\s*(?:conclu[ií]d[ao]|fechad[ao]|cancelad[ao]|finalizad[ao])\s*$"
    manutencoes = await db.manutencoes.find(
        {"status": {"$not": {"$regex": status_encerrado, "$options": "i"}}},
        {"_id": 0},
    ).to_list(1000)
    manut_map = {m["veiculo_id"]: m for m in manutencoes if "veiculo_id" in m}

    for d in docs:
        if not d.get("data_inicio"):
            d["data_inicio"] = d.get("created_at", "").split("T")[0]
            
        if d["veiculo_id"] in manut_map:
            m = manut_map[d["veiculo_id"]]
            d["manutencao"] = {
                "id": m.get("id"),
                "usuario": m.get("created_by") or m.get("usuario") or "Sistema",
                "data": m.get("data_abertura") or m.get("created_at") or ""
            }
            
    return [Acoplamento(**d) for d in docs]

@router.post("", response_model=Acoplamento, status_code=201)
async def criar(body: AcoplamentoCreate, request: Request, user: dict = Depends(require("write"))):
    async def inserir(session):
        await verificar_disponibilidade(body, session)
        v_label, c_label, m_label = await _get_labels(body.veiculo_id, body.carreta_id, body.motorista_id, session)
        agora = now_iso()
        doc = {
            "id": str(uuid.uuid4()),
            "veiculo_id": body.veiculo_id, "veiculo_label": v_label,
            "carreta_id": body.carreta_id, "carreta_label": c_label,
            "motorista_id": body.motorista_id, "motorista_label": m_label,
            "status": "ativo", "completo": bool(body.carreta_id and body.motorista_id),
            "created_at": agora, "updated_at": agora,
            "created_by": user["nome"], "updated_by": user["nome"],
            "data_inicio": body.data_inicio, "data_fim": body.data_fim,
            **{
                f"{campo}_vinculado_em": agora
                for campo, _ in ITENS_ACOPLAMENTO if getattr(body, f"{campo}_id")
            },
        }
        await db.acoplamentos.insert_one(dict(doc), session=session)
        hist_doc = {
            "id": str(uuid.uuid4()),
            "acoplamento_id": doc["id"],
            "conjunto": v_label.split(" ")[0],
            "evento": "Novo Conjunto",
            "item": "conjunto",
            "descricao": f"Criado por {user['nome']}",
            "status": "Acoplado",
            "usuario": user["nome"],
            "created_at": agora,
        }
        await db.acoplamentos_historico.insert_one(hist_doc, session=session)
        return Acoplamento(**doc)

    salvo = await transacao_vinculos(inserir)
    await audit(user, "criar", "acoplamentos", salvo.id, f"Veículo: {salvo.veiculo_label}", request)
    return salvo


@router.get("/historico", response_model=list[HistoricoItem])
async def historico(limit: int = 100, _u: dict = Depends(require("read"))):
    docs = await db.acoplamentos_historico.find({}, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return [HistoricoItem(**d) for d in docs]

@router.put("/{id}", response_model=Acoplamento)
async def atualizar(id: str, body: AcoplamentoCreate, request: Request, user: dict = Depends(require("write"))):
    async def editar(session):
        filtro = {"id": id}
        atual = await db.acoplamentos.find_one(filtro, session=session)
        if not atual:
            raise HTTPException(404, "Acoplamento não encontrado.")
        if atual.get("status") != "ativo":
            raise HTTPException(409, "Este acoplamento já foi encerrado. Atualize a lista.")
        await verificar_disponibilidade(body, session, ignorar_id=id)
        v_label, c_label, m_label = await _get_labels(body.veiculo_id, body.carreta_id, body.motorista_id, session)
        agora = now_iso()
        dados = {
            "veiculo_id": body.veiculo_id, "veiculo_label": v_label,
            "carreta_id": body.carreta_id, "carreta_label": c_label,
            "motorista_id": body.motorista_id, "motorista_label": m_label,
            "data_inicio": body.data_inicio, "data_fim": body.data_fim,
            "completo": bool(body.carreta_id and body.motorista_id),
            "updated_at": agora, "updated_by": user["nome"],
        }
        eventos = []
        for campo, funcao in ITENS_ACOPLAMENTO:
            item_id = getattr(body, f"{campo}_id") or None
            anterior_id = atual.get(f"{campo}_id") or None
            if item_id != anterior_id:
                dados[f"{campo}_vinculado_em"] = agora if item_id else None
                antes = atual.get(f"{campo}_label") or anterior_id or "Sem vínculo"
                depois = dados.get(f"{campo}_label") or item_id or "Sem vínculo"
                eventos.append(evento_historico(
                    atual, user["nome"], agora, f"Alteração de {funcao.lower()}",
                    campo, f"{antes} → {depois}", "Acoplado" if item_id else "Desacoplado",
                ))

        datas = []
        for campo, titulo in (("data_inicio", "Início"), ("data_fim", "Fim")):
            antes = atual.get(campo) or None
            depois = dados.get(campo) or None
            if antes != depois:
                datas.append(f"{titulo}: {antes or '—'} → {depois or '—'}")
        if datas:
            eventos.append(evento_historico(
                atual, user["nome"], agora, "Datas do conjunto alteradas",
                "conjunto", " | ".join(datas), "Acoplado",
            ))

        await db.acoplamentos.update_one(filtro, {"$set": dados}, session=session)
        if eventos:
            await db.acoplamentos_historico.insert_many(eventos, session=session)
        return Acoplamento(**{**atual, **dados})

    salvo = await transacao_vinculos(editar)
    await audit(user, "atualizar", "acoplamentos", id, f"Veículo: {salvo.veiculo_label}", request)
    return salvo


@router.delete("/{id}")
async def excluir(id: str, request: Request, user: dict = Depends(require("write"))):
    async def encerrar(session):
        filtro = {"id": id, "status": "ativo"}
        atual = await db.acoplamentos.find_one(filtro, session=session)
        if not atual:
            raise HTTPException(404, "Acoplamento ativo não encontrado.")
        agora = now_iso()
        await db.acoplamentos.update_one(
            filtro,
            {"$set": {"status": "inativo", "updated_at": agora, "updated_by": user["nome"]}},
            session=session,
        )
        integrantes = " · ".join(
            atual.get(f"{campo}_label") or atual[f"{campo}_id"]
            for campo, _ in ITENS_ACOPLAMENTO if atual.get(f"{campo}_id")
        )
        evento = evento_historico(
            atual, user["nome"], agora, "Conjunto desacoplado",
            "conjunto", integrantes, "Desacoplado",
        )
        await db.acoplamentos_historico.insert_one(evento, session=session)
    await transacao_vinculos(encerrar)
    await audit(user, "excluir", "acoplamentos", id, "Desacoplamento", request)
    return {"ok": True}

@router.get("/{id}/historico", response_model=list[HistoricoItem])
async def historico_item(id: str, _u: dict = Depends(require("read"))):
    docs = await db.acoplamentos_historico.find({"acoplamento_id": id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return [HistoricoItem(**d) for d in docs]
