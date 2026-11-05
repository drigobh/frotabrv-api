import requests

API_URL = "https://frotabrv-api.onrender.com"
url = f"{API_URL}/api/auth/reativar-admin-temporario"

print(f"🔄 Chamando {url}...")
try:
    response = requests.post(url, json={}, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.text}")
    if response.status_code == 200:
        print("✅ Usuário admin reativado com sucesso! Tente fazer login novamente.")
    elif response.status_code == 404:
        print("⚠️ A rota temporária ainda não está no Render. Aguarde mais 2 minutos e tente de novo.")
    else:
        print("❌ Erro inesperado. Verifique o log do Render.")
except Exception as e:
    print(f"❌ Erro de conexão: {e}")