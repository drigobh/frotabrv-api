import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_BACK_PLANOS_500_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "app/backend/models/planos_manutencao.py",
        "app/backend/routers/planos_manutencao.py"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    # 1. Corrigir o Model (garantir que todos os campos estão lá)
    model_path = os.path.join(raiz, "app", "backend", "models", "planos_manutencao.py")
    with open(model_path, 'w', encoding='utf-8') as f:
        f.write('''from pydantic import BaseModel
from typing import Optional

class PlanoManutencaoCreate(BaseModel):
    veiculo_id: Optional[str] = None
    carreta_id: Optional[str] = None
    familia: str
    descricao: str
    tipo_gatilho: str
    tipo_recorrencia: str = "periodico"
    unidade_tempo: Optional[str] = None
    intervalo: float
    ultima_execucao_km: Optional[float] = None
    ultima_execucao_data: Optional[str] = None
    data_abertura: str
    ativo: bool = True

class PlanoManutencao(PlanoManutencaoCreate):
    id: str
    veiculo_label: str
    created_by: str
    created_at: str
''')
    print("✅ Model PlanoManutencao corrigido.")

    # 2. Corrigir o Router (garantir que salve todos os campos)
    router_path = os.path.join(raiz, "app", "backend", "routers", "planos_manutencao.py")
    with open(router_path, 'w', encoding='utf-8') as f:
        f.write('''import uuid
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.planos_manutencao import PlanoManutencaoCreate, PlanoManutencao

router = APIRouter(prefix="/planos-manutencao", tags=["Planos de Manutenção"])

@router.get("", response_model=list[PlanoManutencao])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.planos_manutencao.find({}, {"_id": 0}).to_list(1000)
    return [PlanoManutencao(**d) for d in docs]

@router.post("", response_model=PlanoManutencao, status_code=201)
async def criar(body: PlanoManutencaoCreate, user: dict = Depends(require("write"))):
    # Verifica o veículo (cavalo ou carreta)
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

    doc = body.model_dump()
    doc["veiculo_label"] = label
    
    await db.planos_manutencao.update_one({"id": id}, {"$set": doc})
    doc = await db.planos_manutencao.find_one({"id": id}, {"_id": 0})
    return PlanoManutencao(**doc)

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    await db.planos_manutencao.delete_one({"id": id})
    return {"ok": True}
''')
    print("✅ Router PlanoManutencao corrigido (com suporte a cavalo/carreta).")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso! Faça o git push.")