import os
import re

# ==========================================
# 1. BACKEND: ACEITAR "TODOS" E CORRIGIR BUSCA
# ==========================================
path_backend = os.path.join(os.getcwd(), "app", "backend", "routers", "veiculos.py")

with open(path_backend, "r", encoding="utf-8") as f:
    c_back = f.read()

# Substitui a rota inteira para garantir que o filtro "Todos" funcione
nova_rota = '''
@router.get("/detalhes/{veiculo_id}")
async def detalhes_veiculo_360(veiculo_id: str, mes: str = None, ano: str = None, _u: dict = Depends(require("read"))):
    veiculo = await db.veiculos.find_one({"id": veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado.")

    # Filtro de data
    filtro_data = {}
    if mes and mes != "0" and ano and ano != "0":
        filtro_data = {"data_abastecimento": {"$regex": f"^{ano}-{mes.zfill(2)}"}}

    # Busca os dados
    abastecimentos = await db.abastecimentos.find({"veiculo_id": veiculo_id, **filtro_data}, {"_id": 0}).sort("data_abastecimento", -1).to_list(100)
    manutencoes = await db.manutencoes.find({"veiculo_id": veiculo_id}, {"_id": 0}).to_list(100)
    pneus = await db.pneus.find({"veiculo_id": veiculo_id}, {"_id": 0}).to_list(100)

    # Cálculos
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
'''

padrao = r'@router\.get\("/detalhes/\{veiculo_id\}"\)[\s\S]*?(?=\n@router|\Z)'
if re.search(padrao, c_back):
    c_back = re.sub(padrao, nova_rota, c_back)
    print("✅ Backend: Rota 360º atualizada para aceitar 'Todos'.")

with open(path_backend, "w", encoding="utf-8") as f:
    f.write(c_back)

# ==========================================
# 2. FRONTEND: ADICIONAR "TODOS OS MESES"
# ==========================================
path_frontend = os.path.join(os.getcwd(), "frontend", "src", "pages", "VeiculoDetalhe.tsx")

with open(path_frontend, "r", encoding="utf-8") as f:
    c_front = f.read()

# Adiciona a opção "Todos os Meses" no select
c_front = c_front.replace(
    '{meses.map((m, i) => <option key={m} value={i+1}>{m}</option>)}',
    '<option value={0}>Todos os Meses</option>\n          {meses.map((m, i) => <option key={m} value={i+1}>{m}</option>)}'
)

# Ajusta o estado inicial para "Todos" (0)
c_front = c_front.replace('useState(new Date().getMonth() + 1)', 'useState(0)')

with open(path_frontend, "w", encoding="utf-8") as f:
    f.write(c_front)
    print("✅ Frontend: Opção 'Todos os Meses' adicionada.")

print("\n✅ Correções aplicadas! Faça o git push.")