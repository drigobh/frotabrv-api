from fastapi import APIRouter, Depends
from lib.db import db
from lib.security import require
from datetime import datetime, timedelta

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("")
async def get_dashboard(_u: dict = Depends(require("read"))):
    abastecimentos = await db.abastecimentos.find({}, {"_id": 0}).to_list(5000)
    manutencoes = await db.manutencoes.find({}, {"_id": 0}).to_list(5000)

    # Função para extrair custo de forma segura (tenta varios campos e converte para float)
    def get_custo(m):
        for campo in ["custo", "valor", "preco", "valor_total"]:
            val = m.get(campo)
            if val is not None:
                try:
                    return float(val)
                except (ValueError, TypeError):
                    pass
        return 0.0

    def get_valor_abast(a):
        for campo in ["valor_total", "valor", "preco_total"]:
            val = a.get(campo)
            if val is not None:
                try:
                    return float(val)
                except (ValueError, TypeError):
                    pass
        return 0.0

    total_abastecimento = sum(get_valor_abast(a) for a in abastecimentos)
    total_manutencao = sum(get_custo(m) for m in manutencoes)
    total_geral = total_abastecimento + total_manutencao

    hoje = datetime.now()
    meses_grafico = []
    for i in range(5, -1, -1):
        ano = hoje.year
        mes = hoje.month - i
        while mes <= 0:
            mes += 12
            ano -= 1
        data_ref = datetime(ano, mes, 1)
        mes_ano = data_ref.strftime("%Y-%m")
        label = data_ref.strftime("%b/%y")
        
        v_abast = sum(get_valor_abast(a) for a in abastecimentos if str(a.get("data", "")).startswith(mes_ano))
        v_manut = sum(get_custo(m) for m in manutencoes if str(m.get("data", "")).startswith(mes_ano))
        
        meses_grafico.append({
            "mes": label,
            "abastecimento": v_abast,
            "manutencao": v_manut
        })

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

@router.get("/resumo")
async def resumo_dashboard(_u: dict = Depends(require("read"))):
    # 1. Fornecedores por Estado
    pipeline_estados = [
        {"$match": {"status": "ativo", "estado": {"$ne": None}}},
        {"$group": {"_id": "$estado", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    fornecedores_por_estado = await db.fornecedores.aggregate(pipeline_estados).to_list(100)
    
    # 2. Custos de Manutenção por Mês (últimos 6 meses)
    # Simplificado: pega os últimos 100 registros e agrupa
    manutencoes = await db.manutencoes.find({}, {"custo": 1, "data": 1}).sort("data", -1).to_list(1000)
    custos_por_mes = {}
    for m in manutencoes:
        if m.get("data") and m.get("custo"):
            mes = m["data"][:7] # YYYY-MM
            custos_por_mes[mes] = custos_por_mes.get(mes, 0) + m["custo"]
    custos_manutencao = [{"mes": k, "custo": v} for k, v in sorted(custos_por_mes.items())]

    # 3. Volume de Abastecimentos por Mês
    abastecimentos = await db.abastecimentos.find({}, {"litros": 1, "data": 1}).sort("data", -1).to_list(1000)
    volume_abast = {}
    for a in abastecimentos:
        if a.get("data") and a.get("litros"):
            mes = a["data"][:7]
            volume_abast[mes] = volume_abast.get(mes, 0) + a["litros"]
    volume_abastecimentos = [{"mes": k, "litros": v} for k, v in sorted(volume_abast.items())]

    # 4. Top 5 Fornecedores por Custo de Manutenção (exemplo)
    # Como não temos o valor total por fornecedor facilmente, vamos simular pegando os mais frequentes
    pipeline_top_forn = [
        {"$match": {"status": "ativo"}},
        {"$group": {"_id": "$nome", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    top_fornecedores = await db.fornecedores.aggregate(pipeline_top_forn).to_list(5)

    return {
        "fornecedores_por_estado": [{"estado": item["_id"], "quantidade": item["count"]} for item in fornecedores_por_estado],
        "custos_manutencao": custos_manutencao,
        "volume_abastecimentos": volume_abastecimentos,
        "top_fornecedores": [{"nome": item["_id"], "quantidade": item["count"]} for item in top_fornecedores]
    }

@router.get("/relatorios-manutencao")
async def relatorios_manutencao(_u: dict = Depends(require("read"))):
    # 1. Ratio Preventiva vs. Corretiva
    total = await db.manutencoes.count_documents({})
    preventivas = await db.manutencoes.count_documents({"tipo": "Preventiva"})
    corretivas = await db.manutencoes.count_documents({"tipo": "Corretiva"})
    
    ratio = {
        "total": total,
        "preventivas": preventivas,
        "corretivas": corretivas,
        "percentual_preventiva": (preventivas / total * 100) if total > 0 else 0,
        "percentual_corretiva": (corretivas / total * 100) if total > 0 else 0
    }

    # 2. Manutenções por Faixa de Hodômetro (Agrupado)
    pipeline_km = [
        {"$match": {"km_manutencao": {"$ne": None}}},
        {"$bucket": {
            "groupBy": "$km_manutencao",
            "boundaries": [0, 100000, 200000, 300000, 400000, 500000, 600000, 700000, 800000, 1000000],
            "default": "1000000+",
            "output": {"count": {"$sum": 1}}
        }}
    ]
    faixas = await db.manutencoes.aggregate(pipeline_km).to_list(20)

    # 3. Forecast (Previsão Orçamentária para os próximos 3 meses)
    # Projeta com base na média dos últimos 3 meses
    manutencoes_recentes = await db.manutencoes.find({}, {"custo": 1, "data": 1}).sort("data", -1).to_list(100)
    custos_mensais = {}
    for m in manutencoes_recentes:
        if m.get("data") and m.get("custo"):
            mes = m["data"][:7]
            custos_mensais[mes] = custos_mensais.get(mes, 0) + m["custo"]
    
    ultimos_meses = sorted(custos_mensais.items(), reverse=True)[:3]
    media_mensal = sum(c[1] for c in ultimos_meses) / len(ultimos_meses) if ultimos_meses else 0

    forecast = {
        "media_mensal": media_mensal,
        "proximos_3_meses": media_mensal * 3,
        "proximos_6_meses": media_mensal * 6
    }

    return {
        "ratio": ratio,
        "faixas_km": [{"faixa": str(f["_id"]), "quantidade": f["count"]} for f in faixas],
        "forecast": forecast
    }
