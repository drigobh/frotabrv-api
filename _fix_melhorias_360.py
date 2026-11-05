import os
import re

# ==========================================
# 1. BACKEND: CÁLCULOS E DATAS
# ==========================================
path_backend = os.path.join(os.getcwd(), "app", "backend", "routers", "veiculos.py")

with open(path_backend, "r", encoding="utf-8") as f:
    c_back = f.read()

# Atualiza a rota para trazer os totais e a última manutenção
nova_rota = '''
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
'''

padrao = r'@router\.get\("/detalhes/\{veiculo_id\}"\)[\s\S]*?(?=\n@router|\Z)'
if re.search(padrao, c_back):
    c_back = re.sub(padrao, nova_rota, c_back)
    with open(path_backend, "w", encoding="utf-8") as f:
        f.write(c_back)
    print("✅ Backend: Cálculos e última manutenção adicionados.")

# ==========================================
# 2. FRONTEND: CARDS, DATAS E PNEUS
# ==========================================
path_frontend = os.path.join(os.getcwd(), "frontend", "src", "pages", "VeiculoDetalhe.tsx")

with open(path_frontend, "r", encoding="utf-8") as f:
    c = f.read()

# --- 2.1 Ajusta os KPIs no topo (agora com 6 cards) ---
c = c.replace(
    '<div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">',
    '<div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">'
)
c = c.replace(
    '''<div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-[11px] uppercase tracking-widest text-slate-400">OS Realizadas</p>
          <p className="mt-2 font-mono text-xl font-bold text-slate-100">{manutencoes.length}</p>
        </div>''',
    '''<div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-[11px] uppercase tracking-widest text-slate-400">OS Realizadas</p>
          <p className="mt-2 font-mono text-xl font-bold text-slate-100">{manutencoes.length}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-[11px] uppercase tracking-widest text-slate-400">Litros Abastecidos</p>
          <p className="mt-2 font-mono text-xl font-bold text-sky-400">{num(financeiro.litros_total || 0, 1)} <span className="text-xs text-slate-500">L</span></p>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-[11px] uppercase tracking-widest text-slate-400">Última Manutenção</p>
          <p className="mt-2 font-mono text-sm font-bold text-slate-100">
            {detalhes?.ultima_manutencao ? (detalhes.ultima_manutencao.descricao || "OS") : "—"}
          </p>
          <p className="text-[10px] text-slate-500">
            {detalhes?.ultima_manutencao ? getStr(detalhes.ultima_manutencao, "data", "data_entrada").split("T")[0].split("-").reverse().join("/") : ""}
          </p>
        </div>'''
)

# --- 2.2 Adiciona data na Timeline da Visão Geral ---
c = c.replace(
    '<p className="text-sm text-slate-200">Abastecimento · {num(getVal(a, "litros", "quantidade", "volume"), 1)} L</p>',
    '<p className="text-sm text-slate-200">Abastecimento · {num(getVal(a, "litros", "quantidade", "volume"), 1)} L <span className="text-xs text-slate-500 ml-2">({getStr(a, "data", "data_abastecimento")})</span></p>'
)
c = c.replace(
    '<p className="text-sm text-slate-200">{m.descricao || "Manutenção"}</p>',
    '<p className="text-sm text-slate-200">{m.descricao || "Manutenção"} <span className="text-xs text-slate-500 ml-2">({getStr(m, "data", "data_entrada")})</span></p>'
)

# --- 2.3 Corrige a Data na Grid de Abastecimentos ---
c = c.replace(
    '<td className="px-5 py-3 font-mono">{getStr(a, "data", "data_abastecimento", "data_emissao").split("-").reverse().join("/") || "—"}</td>',
    '<td className="px-5 py-3 font-mono">{getStr(a, "data", "data_abastecimento", "data_emissao").split("T")[0].split("-").reverse().join("/") || "—"}</td>'
)

# --- 2.4 Preenche a Aba de Pneus (posição, custo, recapagem) ---
padrao_pneus = r'\{abaAtiva === "Pneus" && \([\s\S]*?\}\n        \)}'
novo_pneus = '''{abaAtiva === "Pneus" && (
          <div className="p-6">
            {pneus.length === 0 ? (
              <div className="text-center py-8 text-slate-500">
                <Disc className="size-8 mx-auto mb-2 opacity-50" />
                <p>Nenhum pneu instalado neste veículo.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {pneus.map((p: any) => (
                  <div key={p.id} className="glass p-4 rounded-xl border border-slate-700 bg-slate-900/50">
                    <div className="flex justify-between items-start mb-2">
                      <p className="font-bold text-sky-400 text-lg">{p.numero_fogo}</p>
                      <span className="text-xs font-mono text-amber-400">{brl(getVal(p, "custo_aquisicao", "custo_total_atual"))}</span>
                    </div>
                    <p className="text-sm text-slate-300">{p.marca} · {p.medida}</p>
                    <div className="mt-3 space-y-1 border-t border-slate-800 pt-2 text-xs">
                      <p className="flex justify-between"><span className="text-slate-500">Posição:</span> <span className="text-slate-200">{p.posicao || p.equipamento || "—"}</span></p>
                      <p className="flex justify-between"><span className="text-slate-500">Sulco Atual:</span> <span className="text-slate-200">{getVal(p, "profundidade_atual", "sulco_atual")} mm</span></p>
                      <p className="flex justify-between"><span className="text-slate-500">Recapagens:</span> <span className="text-slate-200">{p.n_recap || 0}</span></p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}'''
c = re.sub(padrao_pneus, novo_pneus, c)

with open(path_frontend, "w", encoding="utf-8") as f:
    f.write(c)
    print("✅ Frontend: Cards, datas e aba de pneus atualizados.")

print("\n✅ Tudo pronto! Faça o git push.")