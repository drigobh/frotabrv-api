from fastapi import APIRouter, Depends, HTTPException
from lib.security import require
from lib.db import db
from lib.cadastro_base import build_cadastro_router
from models.cadastros import VeiculoCreate, Veiculo

router = build_cadastro_router(
    prefix="/veiculos", collection="veiculos", entidade="Veículo",
    create_model=VeiculoCreate, out_model=Veiculo,
    unique_field="placa", unique_label="Placa", acop_field="veiculo_id", sort_field="placa"
)






@router.get("/detalhes/{veiculo_id}")
async def detalhes_veiculo_360(veiculo_id: str, mes: str = None, ano: str = None, _u: dict = Depends(require("read"))):
    veiculo = await db.veiculos.find_one({"id": veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado.")

    placa = veiculo.get("placa")
    
    # Busca TODOS os abastecimentos e pneus (sem filtro no banco para não errar o campo)
    # O filtro será feito aqui no Python
    todos_abastecimentos = await db.abastecimentos.find({}, {"_id": 0}).sort("data_abastecimento", -1).to_list(1000)
    todos_pneus = await db.pneus.find({}, {"_id": 0}).to_list(1000)
    
    # Filtra no Python: se o ID for o veiculo_id OU a placa estiver em qualquer campo de texto
    abastecimentos = [
        a for a in todos_abastecimentos 
        if str(a.get("veiculo_id")) == veiculo_id 
        or str(a.get("placa", "")).upper() == str(placa).upper()
        or str(a.get("equipamento", "")).upper() == str(placa).upper()
    ]
    
    pneus = [
        p for p in todos_pneus 
        if str(p.get("veiculo_id")) == veiculo_id 
        or str(p.get("equipamento", "")).upper() == str(placa).upper()
        or str(p.get("placa", "")).upper() == str(placa).upper()
    ]

    # Filtro de data (se aplicável)
    if mes and mes != "0" and ano and ano != "0":
        abastecimentos = [a for a in abastecimentos if str(a.get("data_abastecimento", "")).startswith(f"{ano}-{str(mes).zfill(2)}")]

    manutencoes = await db.manutencoes.find({"veiculo_id": veiculo_id}, {"_id": 0}).to_list(100)

    custo_abastecimento = sum(a.get("valor_total", 0) for a in abastecimentos)
    custo_manutencao = sum(m.get("valor", 0) for m in manutencoes)

    consumo_medio = 0
    if len(abastecimentos) >= 2:
        kms = [a.get("hodometro_km", 0) for a in abastecimentos if a.get("hodometro_km")]
        litros = sum(a.get("litros", 0) for a in abastecimentos)
        if len(kms) >= 2 and litros > 0:
            distancia = max(kms) - min(kms)
            if distancia > 0:
                consumo_medio = distancia / litros

    return {
        "veiculo": veiculo,
        "abastecimentos": abastecimentos,
        "manutencoes": manutencoes,
        "pneus": pneus,
        "financeiro": {
            "custo_total": custo_abastecimento + custo_manutencao,
            "consumo_medio": round(consumo_medio, 2) if consumo_medio > 0 else 0
        }
    }
