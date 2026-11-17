import math
import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.planos_manutencao import PlanoManutencaoCreate, PlanoManutencao

router = APIRouter(prefix="/planos-manutencao", tags=["Planos de Manutenção"])

def validar_plano(body: PlanoManutencaoCreate):
    if bool(body.veiculo_id) == bool(body.carreta_id):
        raise HTTPException(422, "Selecione exatamente um veículo ou uma carreta.")
    if not body.descricao.strip() or not body.familia.strip():
        raise HTTPException(422, "Preencha a família e a descrição do plano.")
    if body.tipo_gatilho not in {"km", "horas", "dias"}:
        raise HTTPException(422, "Selecione um tipo de gatilho válido.")
    if not math.isfinite(body.intervalo) or body.intervalo <= 0:
        raise HTTPException(422, "Informe um intervalo maior que zero.")
    if body.tipo_gatilho == "dias":
        if not float(body.intervalo).is_integer():
            raise HTTPException(422, "O intervalo de calendário deve ser um número inteiro.")
        if body.unidade_tempo not in {None, "dias", "meses", "anos"}:
            raise HTTPException(422, "Selecione dias, meses ou anos para o intervalo.")
    for leitura in (body.ultima_execucao_km, body.ultima_execucao_horas, body.horimetro_atual):
        if leitura is not None and (not math.isfinite(leitura) or leitura < 0):
            raise HTTPException(422, "As leituras de hodômetro e horímetro devem ser válidas e não negativas.")
    if (body.ultima_execucao_horas is not None and body.horimetro_atual is not None
            and body.horimetro_atual < body.ultima_execucao_horas):
        raise HTTPException(422, "O horímetro atual é menor que o da última execução.")
    try:
        date.fromisoformat(body.data_abertura)
        if body.ultima_execucao_data:
            date.fromisoformat(body.ultima_execucao_data)
    except ValueError:
        raise HTTPException(422, "Informe datas válidas para o plano.") from None


@router.get("", response_model=list[PlanoManutencao])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.planos_manutencao.find({}, {"_id": 0}).to_list(1000)
    return [PlanoManutencao(**d) for d in docs]

@router.post("", response_model=PlanoManutencao, status_code=201)
async def criar(body: PlanoManutencaoCreate, user: dict = Depends(require("write"))):
    # Verifica o veículo (cavalo ou carreta)
    validar_plano(body)
    veiculo = None
    label = "—"
    
    if body.veiculo_id:
        veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
        if veiculo:
            label = f"{veiculo.get('placa', '')} - {veiculo.get('modelo', '')}"
    elif body.carreta_id:
        veiculo = await db.carretas.find_one({"id": body.carreta_id}, {"_id": 0})
        if veiculo:
            label = f"{veiculo.get('codigo', '')} - {veiculo.get('tipo', '')}"

    if not veiculo:
        raise HTTPException(404, "Ativo não encontrado")

    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["veiculo_label"] = label
    doc["created_by"] = user["nome"]
    doc["created_at"] = now_iso()
    
    await db.planos_manutencao.insert_one(dict(doc))
    return PlanoManutencao(**doc)

@router.put("/{id}", response_model=PlanoManutencao)
async def atualizar(id: str, body: PlanoManutencaoCreate, user: dict = Depends(require("write"))):
    validar_plano(body)
    veiculo = None
    label = "—"
    
    if body.veiculo_id:
        veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
        if veiculo:
            label = f"{veiculo.get('placa', '')} - {veiculo.get('modelo', '')}"
    elif body.carreta_id:
        veiculo = await db.carretas.find_one({"id": body.carreta_id}, {"_id": 0})
        if veiculo:
            label = f"{veiculo.get('codigo', '')} - {veiculo.get('tipo', '')}"

    if not veiculo:
        raise HTTPException(404, "Ativo não encontrado")
    doc = body.model_dump()
    doc["veiculo_label"] = label
    
    await db.planos_manutencao.update_one({"id": id}, {"$set": doc})
    doc = await db.planos_manutencao.find_one({"id": id}, {"_id": 0})
    if doc is None:
        raise HTTPException(404, "Plano não encontrado")
    return PlanoManutencao(**doc)

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    await db.planos_manutencao.delete_one({"id": id})
    return {"ok": True}
