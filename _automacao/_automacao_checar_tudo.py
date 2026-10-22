import os
import requests

# Configurações
API_URL = "https://frotabrv-api.onrender.com/api"
EMAIL = "admin@frotabrv.com"
SENHA = "admin123"

def checar_local():
    raiz = os.getcwd()
    
    # 1. Checar Abastecimentos.tsx
    caminho_abast = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    print("="*60)
    print("📄 CHECANDO Abastecimentos.tsx (Local):")
    if os.path.exists(caminho_abast):
        with open(caminho_abast, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        if "Maior abastecimento" in conteudo:
            print("✅ O arquivo TEM os novos cards.")
        else:
            print("❌ O arquivo NÃO TEM os novos cards (o script anterior não alterou?).")
    else:
        print("❌ Arquivo não encontrado.")

    # 2. Checar dashboard.py
    caminho_dash = os.path.join(raiz, "app", "backend", "routers", "dashboard.py")
    print("\n" + "="*60)
    print("📄 CHECANDO dashboard.py (Local):")
    if os.path.exists(caminho_dash):
        with open(caminho_dash, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        if "historico_recente=historico_recente" in conteudo:
            print("✅ O dashboard.py TEM o histórico.")
        else:
            print("❌ O dashboard.py NÃO TEM o histórico (só tem historico_recente=[]).")
    else:
        print("❌ Arquivo não encontrado.")

def checar_remoto():
    print("\n" + "="*60)
    print("🌐 CHECANDO API REMOTA (Render):")
    try:
        session = requests.Session()
        res_login = session.post(f"{API_URL}/auth/login", json={"email": EMAIL, "senha": SENHA})
        
        if res_login.status_code != 200:
            print(f"❌ Falha no login: {res_login.status_code}")
            return

        # Checa o Dashboard
        res_dash = session.get(f"{API_URL}/dashboard")
        if res_dash.status_code == 200:
            dados = res_dash.json()
            kpis = dados.get("kpis", [])
            hist = dados.get("historico_recente", [])
            print(f"✅ API Dashboard respondeu 200.")
            print(f"   - KPIs recebidos: {len(kpis)}")
            print(f"   - Histórico recebido: {len(hist)} itens")
        else:
            print(f"❌ Erro ao buscar dashboard: {res_dash.status_code} - {res_dash.text}")

        # Checa o Abastecimento (só a rota para ver se existe)
        res_abast = session.get(f"{API_URL}/abastecimentos/ultimo-km/123")
        print(f"   - Rota de abastecimento (ultimo-km): {res_abast.status_code}")

    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    checar_local()
    checar_remoto()
    