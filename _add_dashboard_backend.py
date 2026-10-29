import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_DASHBOARD_BACKEND_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    arquivos = ["app/backend/routers/dashboard.py"]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "dashboard.py")
    if not os.path.exists(caminho):
        print("❌ Arquivo dashboard.py não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Verifica se a rota de resumo já existe
    if '/resumo' not in c:
        nova_rota = '''
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
'''
        # Insere a rota no final do arquivo (antes do último fecha-chaves, se houver)
        c += nova_rota
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rota /dashboard/resumo criada.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso! Faça o git push.")