import os

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "dashboard.py")
    
    codigo = '''from fastapi import APIRouter, Depends
from lib.db import db
from lib.security import require
from datetime import datetime, timedelta

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("")
async def get_dashboard(_u: dict = Depends(require("read"))):
    # 1. Busca dados
    abastecimentos = await db.abastecimentos.find({}, {"_id": 0}).to_list(5000)
    manutencoes = await db.manutencoes.find({}, {"_id": 0}).to_list(5000)

    # 2. Totais
    total_abastecimento = sum((a.get("valor_total") or 0) for a in abastecimentos)
    total_manutencao = sum((m.get("custo") or 0) for m in manutencoes)
    total_geral = total_abastecimento + total_manutencao

    # 3. Agrupamento Mensal (Últimos 6 meses)
    hoje = datetime.now()
    meses_grafico = []
    for i in range(5, -1, -1):
        # Pega o primeiro dia do mês alvo
        ano = hoje.year
        mes = hoje.month - i
        while mes <= 0:
            mes += 12
            ano -= 1
        
        data_ref = datetime(ano, mes, 1)
        mes_ano = data_ref.strftime("%Y-%m")
        label = data_ref.strftime("%b/%y")
        
        v_abast = sum((a.get("valor_total") or 0) for a in abastecimentos if str(a.get("data", "")).startswith(mes_ano))
        v_manut = sum((m.get("custo") or 0) for m in manutencoes if str(m.get("data", "")).startswith(mes_ano))
        
        meses_grafico.append({
            "mes": label,
            "abastecimento": v_abast,
            "manutencao": v_manut
        })

    # 4. Ranking Top 5
    ranking = {}
    for a in abastecimentos:
        v_id = a.get("veiculo_id")
        if not v_id: continue
        if v_id not in ranking:
            ranking[v_id] = {"label": a.get("veiculo_label", "").split(" · ")[0], "litros": 0, "km": 0}
        
        ranking[v_id]["litros"] += (a.get("litros") or 0)
        ranking[v_id]["km"] += (a.get("km_rodados") or 0)

    top_veiculos = sorted(
        [{"label": v["label"], "media": (v["km"] / v["litros"]) if v["litros"] > 0 else 0} for v in ranking.values()],
        key=lambda x: x["media"],
        reverse=True
    )[:5]

    return {
        "total_abastecimento": total_abastecimento,
        "total_manutencao": total_manutencao,
        "total_geral": total_geral,
        "custos_manutencao": {},
        "abastecimentos": abastecimentos,
        "manutencoes": manutencoes,
        "meses_grafico": meses_grafico,
        "top_veiculos": top_veiculos
    }
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Backend: Rota do Dashboard reescrita com cálculo robusto.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Dashboard.tsx")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Força a atualização do dashboard
    if 'staleTime: 0' not in c:
        c = c.replace(
            'queryKey: ["dashboard"], queryFn: () => apiGet<any>("/dashboard")',
            'queryKey: ["dashboard"], queryFn: () => apiGet<any>("/dashboard"), staleTime: 0, refetchOnMount: true'
        )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Dashboard forçando atualização ao abrir a tela.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)