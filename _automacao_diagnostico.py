import os

def diagnostico():
    raiz = os.getcwd()
    
    # 1. Ler Carretas.tsx
    caminho_carretas = os.path.join(raiz, "frontend", "src", "pages", "Carretas.tsx")
    print("="*50)
    print("📄 CONTEÚDO DO Carretas.tsx:")
    print("="*50)
    if os.path.exists(caminho_carretas):
        with open(caminho_carretas, 'r', encoding='utf-8') as f:
            print(f.read())
    else:
        print("❌ Não encontrado.")

    # 2. Ler App.tsx (apenas a parte de rotas)
    caminho_app = os.path.join(raiz, "frontend", "src", "App.tsx")
    print("\n" + "="*50)
    print("📄 CONTEÚDO DO App.tsx (Rotas e Proteção):")
    print("="*50)
    if os.path.exists(caminho_app):
        with open(caminho_app, 'r', encoding='utf-8') as f:
            print(f.read())
    else:
        print("❌ Não encontrado.")

    # 3. Ler useSession.ts (se existir)
    caminho_session = os.path.join(raiz, "frontend", "src", "hooks", "useSession.ts")
    print("\n" + "="*50)
    print("📄 CONTEÚDO DO useSession.ts (Lógica de Login):")
    print("="*50)
    if os.path.exists(caminho_session):
        with open(caminho_session, 'r', encoding='utf-8') as f:
            print(f.read())
    else:
        print("❌ Não encontrado.")

if __name__ == "__main__":
    diagnostico()