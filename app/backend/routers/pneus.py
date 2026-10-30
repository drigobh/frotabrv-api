import uuid
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.pneus import PneuCreate, Pneu

router = APIRouter(prefix="/pneus", tags=["Pneus"])

@router.get("", response_model=list[Pneu])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.pneus.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
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

# --- ROTAS FIXAS PRIMEIRO (Evita conflito com /{id}) ---
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
# CRUD DE MARCAS
# ==========================================
@router.post("/marcas")
async def criar_marca(body: dict, _u: dict = Depends(require("write"))):
    if not await db.marcas_pneus.find_one({"nome": body.get("nome")}):
        await db.marcas_pneus.insert_one({"id": str(uuid.uuid4()), "nome": body.get("nome")})
    return {"ok": True}

@router.delete("/marcas/{id}")
async def excluir_marca(id: str, _u: dict = Depends(require("delete"))):
    await db.marcas_pneus.delete_one({"id": id})
    return {"ok": True}

# ==========================================
# CRUD DE MEDIDAS
# ==========================================
@router.post("/medidas")
async def criar_medida(body: dict, _u: dict = Depends(require("write"))):
    if not await db.medidas_pneus.find_one({"medida": body.get("medida")}):
        await db.medidas_pneus.insert_one({"id": str(uuid.uuid4()), "medida": body.get("medida")})
    return {"ok": True}

@router.delete("/medidas/{id}")
async def excluir_medida(id: str, _u: dict = Depends(require("delete"))):
    await db.medidas_pneus.delete_one({"id": id})
    return {"ok": True}

# ==========================================
# CRUD DE MODELOS
# ==========================================
@router.post("/modelos")
async def criar_modelo(body: dict, _u: dict = Depends(require("write"))):
    if not await db.modelos_pneus.find_one({"nome": body.get("nome")}):
        await db.modelos_pneus.insert_one({"id": str(uuid.uuid4()), "nome": body.get("nome")})
    return {"ok": True}

@router.delete("/modelos/{id}")
async def excluir_modelo(id: str, _u: dict = Depends(require("delete"))):
    await db.modelos_pneus.delete_one({"id": id})
    return {"ok": True}

# --- ROTAS COM PARÂMETRO POR ÚLTIMO ---
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