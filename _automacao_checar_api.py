import os

def checar_api():
    raiz = os.getcwd()
    
    # 1. Ler frontend/src/lib/api.ts
    caminho_api = os.path.join(raiz, "frontend", "src", "lib", "api.ts")
    print("="*60)
    print("📄 CONTEÚDO DO frontend/src/lib/api.ts:")
    print("="*60)
    if os.path.exists(caminho_api):
        with open(caminho_api, 'r', encoding='utf-8') as f:
            print(f.read())
    else:
        print("❌ Arquivo não encontrado.")

    # 2. Ler frontend/vite.config.ts (para checar o proxy)
    caminho_vite = os.path.join(raiz, "frontend", "vite.config.ts")
    print("\n" + "="*60)
    print("📄 CONTEÚDO DO frontend/vite.config.ts (Proxy):")
    print("="*60)
    if os.path.exists(caminho_vite):
        with open(caminho_vite, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            # Mostra apenas a parte do server/proxy
            if "proxy" in conteudo:
                inicio = conteudo.find("proxy:")
                fim = conteudo.find("}", inicio) + 1
                print(conteudo[inicio:fim])
            else:
                print("⚠️ Não há configuração de proxy no vite.config.ts.")
    else:
        print("❌ Arquivo não encontrado.")

    # 3. Ler backend/server.py (para checar o CORS)
    caminho_server = os.path.join(raiz, "app", "backend", "server.py")
    print("\n" + "="*60)
    print("📄 CONTEÚDO DO app/backend/server.py (CORS):")
    print("="*60)
    if os.path.exists(caminho_server):
        with open(caminho_server, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            inicio = conteudo.find("CORSMiddleware")
            fim = conteudo.find(")", inicio) + 1
            print(conteudo[inicio:fim])
    else:
        print("❌ Arquivo não encontrado.")

if __name__ == "__main__":
    checar_api()