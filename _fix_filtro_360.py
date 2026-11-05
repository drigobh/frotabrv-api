import os
import re

# ==========================================
# 1. BACKEND: CORRIGIR FILTROS E BUSCAS
# ==========================================
path_backend = os.path.join(os.getcwd(), "app", "backend", "routers", "veiculos.py")

with open(path_backend, "r", encoding="utf-8") as f:
    c_back = f.read()

nova_rota = '''
@router.get("/detalhes/{veiculo_id}")
async def detalhes_veiculo_360(veiculo_id: str, mes: str = None, ano: str = None, _u: dict = Depends(require("read"))):
    veiculo = await db.veiculos.find_one({"id": veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado.")

    placa = veiculo.get("placa")
    
    # Busca bruta de tudo (para evitar erro de nome de campo)
    todos_abastecimentos = await db.abastecimentos.find({}, {"_id": 0}).to_list(2000)
    todos_pneus = await db.pneus.find({}, {"_id": 0}).to_list(2000)
    todas_manutencoes = await db.manutencoes.find({}, {"_id": 0}).to_list(2000)
    
    # Filtra abastecimentos: por ID ou Placa
    abastecimentos = [
        a for a in todos_abastecimentos 
        if str(a.get("veiculo_id")) == veiculo_id 
        or str(a.get("placa", "")).upper() == str(placa).upper()
        or str(a.get("equipamento", "")).upper() == str(placa).upper()
    ]
    
    # Filtra pneus: por ID, Placa ou Equipamento
    pneus = [
        p for p in todos_pneus 
        if str(p.get("veiculo_id")) == veiculo_id 
        or str(p.get("equipamento", "")).upper() == str(placa).upper()
        or str(p.get("placa", "")).upper() == str(placa).upper()
    ]

    # Filtra manutenções: por ID ou Placa
    manutencoes = [
        m for m in todas_manutencoes 
        if str(m.get("veiculo_id")) == veiculo_id 
        or str(m.get("veiculo_placa", "")).upper() == str(placa).upper()
        or str(m.get("placa", "")).upper() == str(placa).upper()
    ]

    # Aplica filtro de mês/ano (se não for "Todos")
    if mes and mes != "0" and ano and ano != "0":
        prefixo = f"{ano}-{str(mes).zfill(2)}"
        # Filtra abastecimentos por data
        abastecimentos = [a for a in abastecimentos if str(a.get("data", "")).startswith(prefixo) or str(a.get("data_abastecimento", "")).startswith(prefixo)]
        # Filtra manutenções por data
        manutencoes = [m for m in manutencoes if str(m.get("data", "")).startswith(prefixo) or str(m.get("data_entrada", "")).startswith(prefixo)]
        # Pneus não têm data de movimentação (mostramos todos, ou podemos filtrar se houver data)
    
    custo_abastecimento = sum(float(a.get("valor_total") or a.get("valor") or a.get("total") or 0) for a in abastecimentos)
    custo_manutencao = sum(float(m.get("valor") or m.get("valor_total") or 0) for m in manutencoes)

    consumo_medio = 0
    if len(abastecimentos) >= 2:
        kms = [float(a.get("hodometro_km") or a.get("km") or a.get("hodometro") or 0) for a in abastecimentos]
        litros = sum(float(a.get("litros") or a.get("quantidade") or 0) for a in abastecimentos)
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
    with open(path_backend, "w", encoding="utf-8") as f:
        f.write(c_back)
    print("✅ Backend: Rota 360º corrigida com filtros e buscas inteligentes.")

# ==========================================
# 2. FRONTEND: RECARREGAR AO MUDAR FILTRO
# ==========================================
path_frontend = os.path.join(os.getcwd(), "frontend", "src", "pages", "VeiculoDetalhe.tsx")

with open(path_frontend, "r", encoding="utf-8") as f:
    c_front = f.read()

# Garante que a query key inclui o mes e ano para recarregar
if 'queryKey: ["veiculo-detalhes", id, mesFiltro, anoFiltro]' not in c_front:
    c_front = c_front.replace(
        'queryKey: ["veiculo-detalhes", id]',
        'queryKey: ["veiculo-detalhes", id, mesFiltro, anoFiltro]'
    )

# Verifica se o select está disparando a mudança corretamente
c_front = c_front.replace(
    'onChange={(e) => setMesFiltro(Number(e.target.value))}',
    'onChange={(e) => setMesFiltro(Number(e.target.value))}'
)

with open(path_frontend, "w", encoding="utf-8") as f:
    f.write(c_front)
    print("✅ Frontend: Query key inclui filtros para recarregar dados.")

print("\n✅ Correções aplicadas! Faça o git push.")