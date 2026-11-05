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
    
    todos_abastecimentos = await db.abastecimentos.find({}, {"_id": 0}).to_list(2000)
    todos_pneus = await db.pneus.find({}, {"_id": 0}).to_list(2000)
    todas_manutencoes = await db.manutencoes.find({}, {"_id": 0}).to_list(2000)
    
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

    manutencoes = [
        m for m in todas_manutencoes 
        if str(m.get("veiculo_id")) == veiculo_id 
        or str(m.get("veiculo_placa", "")).upper() == str(placa).upper()
        or str(m.get("placa", "")).upper() == str(placa).upper()
    ]

    if mes and mes != "0" and ano and ano != "0":
        prefixo = f"{ano}-{str(mes).zfill(2)}"
        abastecimentos = [a for a in abastecimentos if str(a.get("data", "")).startswith(prefixo) or str(a.get("data_abastecimento", "")).startswith(prefixo)]
        manutencoes = [m for m in manutencoes if str(m.get("data", "")).startswith(prefixo) or str(m.get("data_entrada", "")).startswith(prefixo)]
    
    custo_abastecimento = sum(float(a.get("valor_total") or a.get("valor") or a.get("total") or 0) for a in abastecimentos)
    custo_manutencao = sum(float(m.get("valor") or m.get("valor_total") or 0) for m in manutencoes)
    litros_total = sum(float(a.get("litros") or a.get("quantidade") or 0) for a in abastecimentos)

    consumo_medio = 0
    if len(abastecimentos) >= 2:
        kms = [float(a.get("hodometro_km") or a.get("km") or a.get("hodometro") or 0) for a in abastecimentos]
        litros = sum(float(a.get("litros") or a.get("quantidade") or 0) for a in abastecimentos)
        if len(kms) >= 2 and litros > 0:
            distancia = max(kms) - min(kms)
            if distancia > 0:
                consumo_medio = distancia / litros

    # Ordena manutenções pela data mais recente
    manutencoes_ordenadas = sorted(
        manutencoes, 
        key=lambda x: str(x.get("data") or x.get("data_entrada") or ""), 
        reverse=True
    )
    ultima_manutencao = manutencoes_ordenadas[0] if manutencoes_ordenadas else None

    return {
        "veiculo": veiculo,
        "abastecimentos": abastecimentos,
        "manutencoes": manutencoes,
        "pneus": pneus,
        "ultima_manutencao": ultima_manutencao,
        "financeiro": {
            "custo_total": custo_abastecimento + custo_manutencao,
            "consumo_medio": round(consumo_medio, 2) if consumo_medio > 0 else 0,
            "litros_total": round(litros_total, 2)
        }
    }
