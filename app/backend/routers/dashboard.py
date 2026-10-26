from fastapi import APIRouter, Depends
from lib.db import db
from lib.security import require
from datetime import datetime, timedelta

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("")
async def get_dashboard(_u: dict = Depends(require("read"))):
    # 1. Buscar Abastecimentos e Manutenções
    abastecimentos = await db.abastecimentos.find({}, {"_id": 0}).to_list(5000)
    manutencoes = await db.manutencoes.find({}, {"_id": 0}).to_list(5000)

    # 2. Calcular totais gerais
    total_abastecimento = sum(a.get("valor_total", 0) for a in abastecimentos)
    total_manutencao = sum(m.get("custo", 0) for m in manutencoes)
    total_geral = total_abastecimento + total_manutencao

    # 3. Agrupar por mês para o gráfico (últimos 6 meses)
    hoje = datetime.now()
    meses_grafico = []
    for i in range(5, -1, -1):
        data_ref = hoje - timedelta(days=30 * i)
        mes_ano = data_ref.strftime("%Y-%m")
        label = data_ref.strftime("%b/%y")
        
        valor_abast = sum(a.get("valor_total", 0) for a in abastecimentos if str(a.get("data", "")).startswith(mes_ano))
        valor_manut = sum(m.get("custo", 0) for m in manutencoes if str(m.get("data", "")).startswith(mes_ano))
        
        meses_grafico.append({
            "mes": label,
            "abastecimento": valor_abast,
            "manutencao": valor_manut
        })

    # 4. Buscar top veículos (Ranking)
    ranking = {}
    for a in abastecimentos:
        v_id = a.get("veiculo_id")
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
