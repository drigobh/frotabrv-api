import urllib.request
import json

def diagnosticar_via_api():
    print("=" * 60)
    print("DIAGNÓSTICO DAS MANUTENÇÕES (VIA API)")
    print("=" * 60)
    
    BASE_URL = "https://frotabrv-api.onrender.com/api"
    
    # ⚠️ ALTERE AQUI COM O SEU E-MAIL E SENHA REAIS:
    email = "seu_email@aqui.com"
    senha = "sua_senha_aqui"
    
    print(f"🔐 Fazendo login com: {email}...")
    login_data = json.dumps({"email": email, "senha": senha}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/login", data=login_data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as res:
            login_res = json.loads(res.read().decode())
            token = login_res.get("token") or login_res.get("access_token")
            if not token:
                print("❌ Token não retornado. Verifique as credenciais.")
                return
            print("✅ Login realizado.")
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return

    print("\n📋 Buscando manutenções...")
    req_manut = urllib.request.Request(f"{BASE_URL}/manutencoes", headers={'Authorization': f'Bearer {token}'})
    
    try:
        with urllib.request.urlopen(req_manut) as res:
            manutencoes = json.loads(res.read().decode())
            
            if not manutencoes:
                print("❌ NENHUMA MANUTENÇÃO ENCONTRADA NO BANCO.")
                return
            
            print(f"✅ {len(manutencoes)} manutenções encontradas. Analisando as 5 mais recentes:\n")
            
            for i, doc in enumerate(manutencoes[:5]):
                print(f"--- REGISTRO {i+1} ---")
                print(f"Data: {doc.get('data')}")
                print(f"Descrição: {doc.get('descricao')}")
                print(f"Campo 'custo': {doc.get('custo')}")
                
                if doc.get('custo') is None:
                    print("⚠️ O CAMPO 'custo' ESTÁ NULO!")
                elif doc.get('custo') == 0:
                    print("⚠️ O CAMPO 'custo' ESTÁ ZERADO!")
                else:
                    print("✅ O campo 'custo' tem valor.")
                
                print(f"Chaves do registro: {list(doc.keys())}\n")
                
    except Exception as e:
        print(f"❌ Erro ao buscar manutenções: {e}")

    print("=" * 60)
    print("FIM DO DIAGNÓSTICO")

if __name__ == "__main__":
    diagnosticar_via_api()