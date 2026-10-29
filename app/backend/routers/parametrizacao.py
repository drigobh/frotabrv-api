from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.parametrizacao import ParametrizacaoBase, Parametrizacao

router = APIRouter(prefix="/parametrizacao", tags=["parametrizacao"])

@router.get("/meta", response_model=ParametrizacaoBase)
async def obter_meta(_u: dict = Depends(require("read"))):
    config = await db.parametrizacoes.find_one({"id": "meta_abastecimento"}, {"_id": 0})
    if not config:
        return ParametrizacaoBase(meta_abastecimento_ativo=False, meta_abastecimento_valor=2.5)
    return ParametrizacaoBase(
        meta_abastecimento_ativo=config.get("meta_abastecimento_ativo", False),
        meta_abastecimento_valor=config.get("meta_abastecimento_valor", 2.5),
        mostrar_seed_fornecedores=config.get("mostrar_seed_fornecedores", False)
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
            "updated_at": now_iso()
        }},
        upsert=True
    )
    return body
