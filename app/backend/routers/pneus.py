import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.pneus import PneuCreate, Pneu

router = APIRouter(prefix="/pneus", tags=["Pneus"])

def normalizar_tipo(tipo_raw: str) -> str:
    t = str(tipo_raw or "").strip().upper()
    if t in ("LISO", "BORRACHUDO", "MISTO", "MISTA"):
        return "Misto"
    if t == "DIRECIONAL":
        return "Direcional"
    if t in ("TRACAO", "TRAÇÃO"):
        return "Tração"
    if t == "BANDA":
        return "Banda"
    return "Misto"

@router.get("", response_model=list[Pneu])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.pneus.find({}, {"_id": 0}).sort("created_at", -1).to_list(2000)
    return [Pneu(**d) for d in docs]

@router.post("", response_model=Pneu, status_code=201)
async def criar(body: PneuCreate, user: dict = Depends(require("write"))):
    existente = await db.pneus.find_one({"numero_fogo": body.numero_fogo})
    if existente:
        raise HTTPException(409, "Este número de fogo já está cadastrado.")
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    doc["created_by"] = user["nome"]
    await db.pneus.insert_one(dict(doc))
    return Pneu(**doc)

# ==========================================
# ROTA DE IMPORTAÇÃO (Antes de /{id})
# ==========================================
@router.post("/importar")
async def importar_pneus(body: List[dict], user: dict = Depends(require("write"))):
    inseridos = 0
    erros = []
    
    for item in body:
        try:
            if not item.get("numero_fogo") or not item.get("marca"):
                continue
                
            existente = await db.pneus.find_one({"numero_fogo": item["numero_fogo"]})
            if existente:
                erros.append(f"Pneu {item['numero_fogo']} já existe.")
                continue
            
            # Garante que marca, modelo e medida existam nas tabelas de apoio
            marca_nome = item.get("marca", "").strip()
            modelo_nome = item.get("modelo", "").strip()
            medida_nome = item.get("medida", "").strip()
            
            if marca_nome and not await db.marcas_pneus.find_one({"nome": marca_nome}):
                await db.marcas_pneus.insert_one({"id": str(uuid.uuid4()), "nome": marca_nome})
            if modelo_nome and not await db.modelos_pneus.find_one({"nome": modelo_nome}):
                await db.modelos_pneus.insert_one({"id": str(uuid.uuid4()), "nome": modelo_nome})
            if medida_nome and not await db.medidas_pneus.find_one({"medida": medida_nome}):
                await db.medidas_pneus.insert_one({"id": str(uuid.uuid4()), "medida": medida_nome})
                
            doc = {
                "id": str(uuid.uuid4()),
                "numero_fogo": item.get("numero_fogo"),
                "marca": marca_nome,
                "modelo": modelo_nome,
                "medida": medida_nome,
                "dot": item.get("dot", ""),
                "tipo": normalizar_tipo(item.get("tipo", "Misto")),
                "status": item.get("status", "Estoque"),
                "custo_aquisicao": float(item.get("custo_aquisicao", 0)),
                "observacoes": item.get("observacoes", ""),
                "equipamento": item.get("equipamento", ""),
                "posicao": item.get("posicao", ""),
                "banda_rod": item.get("banda_rod", ""),
                "estrutura": item.get("estrutura", ""),
                "n_serie": item.get("n_serie", ""),
                "n_recap": item.get("n_recap", ""),
                "data_compra": item.get("data_compra", ""),
                "data_descarte": item.get("data_descarte", ""),
                "custo_total_atual": float(item.get("custo_total_atual", 0)),
                "profundidade_atual": float(item.get("profundidade_atual", 0)),
                "uso_atual": item.get("uso_atual", ""),
                "custo_por_km": float(item.get("custo_por_km", 0)),
                "km_posicao": float(item.get("km_posicao", 0)),
                "veiculo_id": item.get("veiculo_id"),
                "carreta_id": item.get("carreta_id"),
                "created_at": now_iso(),
                "created_by": user["nome"],
            }
            await db.pneus.insert_one(doc)
            inseridos += 1
        except Exception as e:
            erros.append(f"Erro no pneu {item.get('numero_fogo')}: {str(e)}")
            
    return {"ok": True, "inseridos": inseridos, "erros": erros}

# ==========================================
# ROTAS FIXAS (Antes de /{id})
# ==========================================
@router.get("/marcas")
async def listar_marcas(_u: dict = Depends(require("read"))):
    docs = await db.marcas_pneus.find({}, {"_id": 0}).sort("nome", 1).to_list(500)
    return docs

@router.get("/medidas")
async def listar_medidas(_u: dict = Depends(require("read"))):
    docs = await db.medidas_pneus.find({}, {"_id": 0}).sort("medida", 1).to_list(500)
    return docs

@router.get("/modelos")
async def listar_modelos(_u: dict = Depends(require("read"))):
    docs = await db.modelos_pneus.find({}, {"_id": 0}).sort("nome", 1).to_list(500)
    return docs

@router.get("/dashboard")
async def dashboard_pneus(_u: dict = Depends(require("read"))):
    pneus = await db.pneus.find({}, {"_id": 0}).to_list(2000)
    
    total = len(pneus)
    aplicados = sum(1 for p in pneus if p.get("status") == "Aplicado")
    sucateados = sum(1 for p in pneus if p.get("status") == "Sucateado")
    sulco_critico = sum(1 for p in pneus if p.get("sulco_atual") is not None and p.get("sulco_atual") <= 3.0)
    
    marcas = {}
    for p in pneus:
        m = p.get("marca") or "Desconhecida"
        marcas[m] = marcas.get(m, 0) + 1
    
    top_marcas = [{"marca": k, "qtd": v} for k, v in sorted(marcas.items(), key=lambda item: item[1], reverse=True)[:5]]
    
    return {
        "total": total,
        "aplicados": aplicados,
        "sucateados": sucateados,
        "sulco_critico": sulco_critico,
        "top_marcas": top_marcas
    }

@router.post("/seed")
async def seed_pneus(_u: dict = Depends(require("write"))):
    marcas = ["Michelin", "Bridgestone", "Pirelli", "Goodyear", "Continental", "Bandag"]
    for m in marcas:
        if not await db.marcas_pneus.find_one({"nome": m}):
            await db.marcas_pneus.insert_one({"id": str(uuid.uuid4()), "nome": m})
            
    medidas = ["295/80 R22.5", "275/80 R22.5", "11R22.5", "12R22.5"]
    for m in medidas:
        if not await db.medidas_pneus.find_one({"medida": m}):
            await db.medidas_pneus.insert_one({"id": str(uuid.uuid4()), "medida": m})

    modelos = ["X Multi Z", "X Line Energy", "R268", "M840", "G580"]
    for m in modelos:
        if not await db.modelos_pneus.find_one({"nome": m}):
            await db.modelos_pneus.insert_one({"id": str(uuid.uuid4()), "nome": m})
            
    return {"ok": True, "message": "Carga inicial de pneus realizada."}

# ==========================================
# ROTAS DE EDIÇÃO/EXCLUSÃO (Por último)
# ==========================================

@router.delete("/limpar")
async def limpar_pneus(_u: dict = Depends(require("delete"))):
    await db.pneus.delete_many({})
    return {"ok": True, "message": "Todos os pneus foram removidos."}

@router.put("/{id}", response_model=Pneu)
async def atualizar(id: str, body: PneuCreate, user: dict = Depends(require("write"))):
    existe = await db.pneus.find_one({"id": id})
    if not existe:
        raise HTTPException(404, "Pneu não encontrado.")
    doc = body.model_dump()
    doc["updated_at"] = now_iso()
    doc["updated_by"] = user["nome"]
    await db.pneus.update_one({"id": id}, {"$set": doc})
    doc = await db.pneus.find_one({"id": id}, {"_id": 0})
    return Pneu(**doc)

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    await db.pneus.delete_one({"id": id})
    return {"ok": True}