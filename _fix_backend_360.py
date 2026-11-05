import os

path = os.path.join(os.getcwd(), "app", "backend", "routers", "veiculos.py")

if not os.path.exists(path):
    print("❌ Arquivo veiculos.py não encontrado.")
else:
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    # Adiciona a rota de detalhes 360 se ela não existir
    if "/detalhes/{veiculo_id}" not in c:
        rota_360 = '''

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
'''
        c += rota_360
        # Garante que o HTTPException está importado
        if "HTTPException" not in c:
            c = c.replace("from fastapi import APIRouter, Depends", "from fastapi import APIRouter, Depends, HTTPException")
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(c)
        print("✅ Backend: Rota /veiculos/detalhes/{id} criada.")
    else:
        print("ℹ️ A rota já existia no backend.")