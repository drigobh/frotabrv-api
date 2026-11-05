from fastapi import APIRouter, Depends, HTTPException
from lib.security import require
from lib.cadastro_base import build_cadastro_router
from models.cadastros import VeiculoCreate, Veiculo

router = build_cadastro_router(
    prefix="/veiculos", collection="veiculos", entidade="Veículo",
    create_model=VeiculoCreate, out_model=Veiculo,
    unique_field="placa", unique_label="Placa", acop_field="veiculo_id", sort_field="placa"
)


@router.get("/detalhes/{veiculo_id}")
async def detalhes_veiculo_360(veiculo_id: str, _u: dict = Depends(require("read"))):
    # 1. Busca o veículo
    veiculo = await db.veiculos.find_one({"id": veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado.")

    # 2. Busca abastecimentos (últimos 10)
    abastecimentos = await db.abastecimentos.find(
        {"veiculo_id": veiculo_id}, {"_id": 0}
    ).sort("data_abastecimento", -1).to_list(10)

    # 3. Busca manutenções
    manutencoes = await db.manutencoes.find(
        {"veiculo_id": veiculo_id}, {"_id": 0}
    ).to_list(50)

    # 4. Busca pneus alocados neste veículo
    pneus = await db.pneus.find(
        {"veiculo_id": veiculo_id}, {"_id": 0}
    ).to_list(50)

    # Cálculos
    custo_abastecimento = sum(a.get("valor_total", 0) for a in abastecimentos)
    custo_manutencao = sum(m.get("valor", 0) for m in manutencoes)
    
    return {
        "veiculo": veiculo,
        "abastecimentos": abastecimentos,
        "manutencoes": manutencoes,
        "pneus": pneus,
        "financeiro": {
            "custo_total": custo_abastecimento + custo_manutencao,
            "custo_abastecimento": custo_abastecimento,
            "custo_manutencao": custo_manutencao
        }
    }
