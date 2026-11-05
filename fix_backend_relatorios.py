import os

path = os.path.join(os.getcwd(), "app", "backend", "routers", "pneus.py")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Adiciona a rota de relatórios no final do arquivo (antes do último router)
rotas_relatorios = '''

@router.get("/relatorios/desempenho-marcas")
async def relatorio_desempenho_marcas(_u: dict = Depends(require("read"))):
    pipeline = [
        {"$match": {"status": "Sucateado"}},
        {"$group": {
            "_id": "$marca",
            "total_pneus": {"$sum": 1},
            "km_total": {"$sum": "$km_posicao"},
            "custo_total": {"$sum": "$custo_total_atual"}
        }},
        {"$project": {
            "marca": "$_id",
            "total_pneus": 1,
            "km_medio": {"$divide": ["$km_total", "$total_pneus"]},
            "custo_medio": {"$divide": ["$custo_total", "$total_pneus"]},
            "_id": 0
        }},
        {"$sort": {"km_medio": -1}}
    ]
    resultado = await db.pneus.aggregate(pipeline).to_list(100)
    return resultado

@router.get("/relatorios/alertas")
async def relatorio_alertas(_u: dict = Depends(require("read"))):
    # Pneus rodando com sulco crítico (<= 3mm)
    sulco_critico = await db.pneus.find({"status": "Aplicado", "profundidade_atual": {"$lte": 3}}, {"_id": 0}).to_list(100)
    # Pneus que estão na borracharia há muito tempo (pode ser melhorado depois com datas)
    na_oficina = await db.pneus.find({"status": {"$in": ["Recapagem", "Conserto"]}}, {"_id": 0}).to_list(100)
    return {"sulco_critico": sulco_critico, "na_oficina": na_oficina}

@router.get("/relatorios/financeiro")
async def relatorio_financeiro(_u: dict = Depends(require("read"))):
    pipeline = [
        {"$group": {
            "_id": "$status",
            "quantidade": {"$sum": 1},
            "custo_total": {"$sum": "$custo_aquisicao"}
        }}
    ]
    resultado = await db.pneus.aggregate(pipeline).to_list(100)
    return resultado
'''
if "@router.get(\"/relatorios/desempenho-marcas\")" not in c:
    c += rotas_relatorios
    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("✅ Backend: Rotas de relatórios adicionadas com sucesso.")
else:
    print("ℹ️ Backend: Rotas de relatórios já existem.")