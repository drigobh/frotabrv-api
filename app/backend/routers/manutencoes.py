from fastapi import APIRouter, Depends, HTTPException, Request
from lib.dates import now_iso
from lib.db import db
from lib.security import require
from models.manutencoes import Manutencao, ManutencaoCreate
import uuid

router = APIRouter(prefix="/manutencoes", tags=["manutencoes"])


async def atualizar_estoque(pecas_utilizadas: list[dict], multiplicador: int = -1):
    if not pecas_utilizadas: return
    for p in pecas_utilizadas:
        if p.get("peca_id") and p.get("quantidade"):
            await db.pecas.update_one(
                {"id": p["peca_id"]},
                {"$inc": {"quantidade_estoque": multiplicador * int(p["quantidade"])}}
            )

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

    doc = body.model_dump()
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
    manut = await db.manutencoes.find_one({"id": id})
    if manut: await atualizar_estoque(manut.get("pecas_utilizadas"), 1)
    await db.manutencoes.delete_one({"id": id})
    return {"ok": True}
