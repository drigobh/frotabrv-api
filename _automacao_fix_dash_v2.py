import os

def fix_backend_dashboard(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "dashboard.py")
    
    codigo = '''from fastapi import APIRouter, Depends
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
        ranking[v_id]["litros"] += a.get("litros", 0)
        ranking[v_id]["km"] += a.get("km_rodados", 0)

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
    print("✅ Backend: Rota do dashboard reescrita com agregação de manutenções.")

def fix_frontend_dashboard(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Dashboard.tsx")
    if not os.path.exists(caminho):
        print("❌ Arquivo Dashboard.tsx não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Substitui o bloco de gráfico antigo para usar os novos dados
    # Procura por 'Custos operacionais' para isolar o trecho do gráfico
    if 'Custos operacionais' in c:
        # Vou trocar a chamada do gráfico para usar a nova estrutura 'meses_grafico'
        c = c.replace(
            'data={[{ name: "Custo", valor: dados?.total_geral || 0 }]}',
            'data={dados?.meses_grafico || []}'
        )
        # Certifica de adicionar os bares de Manutenção e Abastecimento se for Recharts
        if 'BarChart' in c and 'Bar' in c:
            c = c.replace(
                '<Bar dataKey="valor" fill="#0ea5e9" />',
                '''<Bar dataKey="abastecimento" stackId="a" fill="#0ea5e9" name="Combustível" />
                <Bar dataKey="manutencao" stackId="a" fill="#f59e0b" name="Manutenção" />'''
            )
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Dashboard.tsx ajustado para ler os dados combinados.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend_dashboard(raiz)
    fix_frontend_dashboard(raiz)