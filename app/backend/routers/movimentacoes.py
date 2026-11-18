from fastapi import APIRouter, Depends, HTTPException
from lib.db import client, db
from lib.security import require
from lib.dates import now_iso
from models.movimentacoes import MovimentacaoCreate, Movimentacao, InventarioPayload, Inventario
import uuid

router = APIRouter(prefix="/estoque", tags=["movimentacoes"])

@router.get("/movimentacoes", response_model=list[Movimentacao])
async def listar_movimentacoes(_u: dict = Depends(require("read"))):
    docs = await db.movimentacoes.find({}, {"_id": 0}).sort("data_hora", -1).to_list(2000)
    return docs

@router.post("/movimentacoes", response_model=Movimentacao, status_code=201)
async def criar_movimentacao(body: MovimentacaoCreate, user: dict = Depends(require("write"))):
    if body.quantidade <= 0:
        raise HTTPException(422, "Informe uma quantidade positiva.")

    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["usuario_nome"] = user.get("nome", user.get("email", "Sistema"))
    doc["data_hora"] = now_iso()

    if body.fornecedor_id:
        forn = await db.fornecedores.find_one({"id": body.fornecedor_id}, {"_id": 0})
        doc["fornecedor_nome"] = forn["nome"] if forn else None

    if body.veiculo_id:
        veic = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
        doc["destino_nome"] = f"Veículo: {veic['placa']}" if veic else None
    elif body.carreta_id:
        carr = await db.carretas.find_one({"id": body.carreta_id}, {"_id": 0})
        doc["destino_nome"] = f"Carreta: {carr['placa']}" if carr else None

    async def salvar(session):
        peca = await db.pecas.find_one_and_update(
            {"id": body.peca_id, "quantidade_estoque": {"$gte": body.quantidade}},
            {"$inc": {"quantidade_estoque": -body.quantidade}},
            session=session,
        )
        if not peca:
            if not await db.pecas.find_one({"id": body.peca_id}, session=session):
                raise HTTPException(404, "Peça não encontrada")
            raise HTTPException(400, "Quantidade insuficiente em estoque.")
        movimento = {**doc, "peca_nome": peca["nome"]}
        await db.movimentacoes.insert_one(movimento, session=session)
        return movimento

    async with await client.start_session() as session:
        return await session.with_transaction(salvar)


@router.get("/inventarios", response_model=list[Inventario])
async def listar_inventarios(_u: dict = Depends(require("read"))):
    docs = await db.inventarios.find({}, {"_id": 0}).sort("data_hora", -1).to_list(2000)
    return docs

@router.post("/inventario")
async def realizar_inventario(body: InventarioPayload, user: dict = Depends(require("write"))):
    if len({item.peca_id for item in body.itens}) != len(body.itens):
        raise HTTPException(422, "Informe cada peça apenas uma vez no inventário.")
    if any(min(item.qtd_anterior, item.qtd_fisica) < 0 for item in body.itens):
        raise HTTPException(422, "As quantidades do inventário devem ser maiores ou iguais a zero.")

    async def salvar(session):
        ajustes = []
        for item in body.itens:
            peca = await db.pecas.find_one({"id": item.peca_id}, session=session)
            if not peca:
                raise HTTPException(404, "Peça do inventário não encontrada.")
            if peca.get("quantidade_estoque") != item.qtd_anterior:
                raise HTTPException(409, f"O saldo de {peca['nome']} mudou. Atualize a contagem e tente novamente.")
            if item.qtd_anterior == item.qtd_fisica:
                continue

            await db.pecas.update_one(
                {"_id": peca["_id"]}, {"$set": {"quantidade_estoque": item.qtd_fisica}}, session=session,
            )
            ajustes.append({**item.model_dump(), "peca_nome": peca["nome"]})
            await db.movimentacoes.insert_one({
                "id": str(uuid.uuid4()),
                "peca_id": item.peca_id,
                "peca_nome": peca["nome"],
                "quantidade": abs(item.qtd_fisica - item.qtd_anterior),
                "motivo": "Inventário Cíclico",
                "observacao": f"Ajuste: {item.qtd_anterior} -> {item.qtd_fisica}",
                "usuario_nome": user.get("nome", "Sistema"),
                "data_hora": now_iso(),
            }, session=session)

        if ajustes:
            await db.inventarios.insert_one({
                "id": str(uuid.uuid4()),
                "data_hora": now_iso(),
                "usuario_nome": user.get("nome", user.get("email", "Sistema")),
                "total_ajustes": len(ajustes),
                "itens": ajustes,
            }, session=session)
        return {"ok": True, "ajustes": len(ajustes)}

    async with await client.start_session() as session:
        return await session.with_transaction(salvar)


@router.delete("/inventarios/{id}")
async def excluir_inventario(id: str, _u: dict = Depends(require("delete"))):
    await db.inventarios.delete_one({"id": id})
    return {"ok": True}


@router.post("/inventarios/{id}/reverter")
async def reverter_inventario(id: str, user: dict = Depends(require("write"))):
    async def salvar(session):
        inv = await db.inventarios.find_one_and_delete({"id": id}, session=session)
        if not inv:
            raise HTTPException(404, "Inventário não encontrado")

        for item in inv["itens"]:
            diff = item["qtd_fisica"] - item["qtd_anterior"]
            if not diff:
                continue

            resultado = await db.pecas.update_one(
                {"id": item["peca_id"], "quantidade_estoque": {"$gte": max(diff, 0)}},
                {"$inc": {"quantidade_estoque": -diff}},
                session=session,
            )
            if not resultado.matched_count:
                raise HTTPException(409, f"Peça indisponível ou saldo insuficiente para reverter {item['peca_nome']}.")

            await db.movimentacoes.insert_one({
                "id": str(uuid.uuid4()),
                "peca_id": item["peca_id"],
                "peca_nome": item["peca_nome"],
                "quantidade": abs(diff),
                "motivo": "Reversão de Inventário",
                "observacao": f"Revertendo ajuste do inventário de {inv['data_hora'][:10]}",
                "usuario_nome": user.get("nome", "Sistema"),
                "data_hora": now_iso(),
            }, session=session)
        return {"ok": True}

    async with await client.start_session() as session:
        return await session.with_transaction(salvar)
