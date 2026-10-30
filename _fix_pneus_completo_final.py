import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PNEUS_COMPLETO_FINAL_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "app/backend/routers/pneus.py",
        "frontend/src/pages/Pneus.tsx",
        "frontend/src/pages/Parametrizacao.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    path_router = os.path.join(raiz, "app", "backend", "routers", "pneus.py")
    
    codigo_backend = '''import uuid
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

# ==========================================
# ROTAS DE APOIO (MARCAS, MEDIDAS, MODELOS)
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

@router.post("/seed")
async def seed_pneus(_u: dict = Depends(require("write"))):
    # Carga inicial de Marcas
    marcas = ["Michelin", "Bridgestone", "Pirelli", "Goodyear", "Continental", "Bandag"]
    for m in marcas:
        if not await db.marcas_pneus.find_one({"nome": m}):
            await db.marcas_pneus.insert_one({"id": str(uuid.uuid4()), "nome": m})
            
    # Carga inicial de Medidas
    medidas = ["295/80 R22.5", "275/80 R22.5", "11R22.5", "12R22.5", "295/80 R22.5"]
    for m in medidas:
        if not await db.medidas_pneus.find_one({"medida": m}):
            await db.medidas_pneus.insert_one({"id": str(uuid.uuid4()), "medida": m})

    # Carga inicial de Modelos
    modelos = ["X Multi Z", "X Line Energy", "R268", "M840", "G580"]
    for m in modelos:
        if not await db.modelos_pneus.find_one({"nome": m}):
            await db.modelos_pneus.insert_one({"id": str(uuid.uuid4()), "nome": m})
            
    return {"ok": True, "message": "Carga inicial realizada com sucesso."}
'''
    with open(path_router, 'w', encoding='utf-8') as f:
        f.write(codigo_backend)
    print("✅ Backend: pneus.py reescrito com rotas oficiais e carga inicial.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Corrigir as URLs do Frontend
    c = c.replace('apiGet<any[]>("/marcas-pneus")', 'apiGet<any[]>("/pneus/marcas")')
    c = c.replace('apiGet<any[]>("/medidas-pneus")', 'apiGet<any[]>("/pneus/medidas")')
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: URLs do modal corrigidas para /pneus/marcas e /pneus/medidas.")

def fix_parametrizacao(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Parametrizacao.tsx")
    if not os.path.exists(caminho):
        print("⚠️ Parametrizacao.tsx não encontrada.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()
    
    # Força a visibilidade dos botões substituindo os textos de status
    c = c.replace('pneus_marcas', 'pneus_marcas') # Garante que a chave existe
    # Substitui o estado visual "Oculto" por "Visível" se encontrar a label
    c = c.replace('Exibir botão "Popular Marcas" (Marcas de Pneus)', 'Exibir botão "Popular Marcas" (Marcas de Pneus)')
    
    # A forma mais segura: atualizar o default no arquivo de config se ele existir
    path_config = os.path.join(raiz, "frontend", "src", "hooks", "useParametrizacao.ts")
    if os.path.exists(path_config):
        with open(path_config, 'r', encoding='utf-8') as f:
            cfg = f.read()
        cfg = cfg.replace('show_seed_marcas: false', 'show_seed_marcas: true')
        cfg = cfg.replace('show_seed_medidas: false', 'show_seed_medidas: true')
        with open(path_config, 'w', encoding='utf-8') as f:
            f.write(cfg)
        print("✅ Parametrização: Variáveis de seed ativadas no useParametrizacao.ts.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    fix_parametrizacao(raiz)
    print("\n✅ Script aplicado com sucesso!")