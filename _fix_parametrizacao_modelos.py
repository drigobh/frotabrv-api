import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PARAM_MODELOS_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "app/backend/models/parametrizacao.py",
        "app/backend/routers/parametrizacao.py"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_model(raiz):
    caminho = os.path.join(raiz, "app", "backend", "models", "parametrizacao.py")
    codigo = '''from pydantic import BaseModel

class ParametrizacaoBase(BaseModel):
    meta_abastecimento_ativo: bool = False
    meta_abastecimento_valor: float = 2.5
    mostrar_seed_fornecedores: bool = False
    mostrar_seed_medidas: bool = False
    mostrar_seed_marcas: bool = False
    mostrar_seed_modelos: bool = False
    mostrar_seed_templates: bool = False
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Model ParametrizacaoBase atualizado (com mostrar_seed_modelos).")

def fix_router(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "parametrizacao.py")
    codigo = '''from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.parametrizacao import ParametrizacaoBase

router = APIRouter(prefix="/parametrizacao", tags=["parametrizacao"])

@router.get("/meta", response_model=ParametrizacaoBase)
async def obter_meta(_u: dict = Depends(require("read"))):
    config = await db.parametrizacoes.find_one({"id": "meta_abastecimento"}, {"_id": 0})
    if not config:
        return ParametrizacaoBase()
    return ParametrizacaoBase(
        meta_abastecimento_ativo=config.get("meta_abastecimento_ativo", False),
        meta_abastecimento_valor=config.get("meta_abastecimento_valor", 2.5),
        mostrar_seed_fornecedores=config.get("mostrar_seed_fornecedores", False),
        mostrar_seed_medidas=config.get("mostrar_seed_medidas", False),
        mostrar_seed_marcas=config.get("mostrar_seed_marcas", False),
        mostrar_seed_modelos=config.get("mostrar_seed_modelos", False),
        mostrar_seed_templates=config.get("mostrar_seed_templates", False)
    )

@router.put("/meta", response_model=ParametrizacaoBase)
async def atualizar_meta(body: ParametrizacaoBase, _u: dict = Depends(require("write"))):
    await db.parametrizacoes.update_one(
        {"id": "meta_abastecimento"},
        {"$set": {
            "id": "meta_abastecimento",
            "meta_abastecimento_ativo": body.meta_abastecimento_ativo,
            "meta_abastecimento_valor": body.meta_abastecimento_valor,
            "mostrar_seed_fornecedores": body.mostrar_seed_fornecedores,
            "mostrar_seed_medidas": body.mostrar_seed_medidas,
            "mostrar_seed_marcas": body.mostrar_seed_marcas,
            "mostrar_seed_modelos": body.mostrar_seed_modelos,
            "mostrar_seed_templates": body.mostrar_seed_templates,
            "updated_at": now_iso()
        }},
        upsert=True
    )
    return body
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Router parametrizacao.py atualizado (com mostrar_seed_modelos).")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_model(raiz)
    fix_router(raiz)
    print("\n✅ Script aplicado com sucesso! Faça o git push para o Render.")