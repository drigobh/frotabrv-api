import os

def ler_abastecimentos():
    raiz = os.getcwd()
    
    # 1. Ler o frontend
    caminho_front = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    print("="*60)
    print("📄 CONTEÚDO DO Abastecimentos.tsx (Frontend):")
    print("="*60)
    if os.path.exists(caminho_front):
        with open(caminho_front, 'r', encoding='utf-8') as f:
            print(f.read())
    else:
        print("❌ Abastecimentos.tsx não encontrado.")

    # 2. Ler o backend
    caminho_back = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    print("\n" + "="*60)
    print("📄 CONTEÚDO DO abastecimentos.py (Backend):")
    print("="*60)
    if os.path.exists(caminho_back):
        with open(caminho_back, 'r', encoding='utf-8') as f:
            print(f.read())
    else:
        print("❌ abastecimentos.py não encontrado.")

if __name__ == "__main__":
    ler_abastecimentos()