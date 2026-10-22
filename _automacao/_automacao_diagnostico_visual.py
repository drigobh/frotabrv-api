import os

def diagnosticar():
    raiz = os.getcwd()
    
    # 1. Ler KpiCard.tsx (para ver as classes de estilo)
    caminho_kpi = os.path.join(raiz, "frontend", "src", "components", "dashboard", "KpiCard.tsx")
    print("="*60)
    print("📄 CONTEÚDO DO KpiCard.tsx:")
    print("="*60)
    if os.path.exists(caminho_kpi):
        with open(caminho_kpi, 'r', encoding='utf-8') as f:
            print(f.read())
    else:
        print("❌ KpiCard.tsx não encontrado.")

    # 2. Ler AppLayout.tsx (para entender a proteção de rotas)
    caminho_layout = os.path.join(raiz, "frontend", "src", "components", "layout", "AppLayout.tsx")
    print("\n" + "="*60)
    print("📄 CONTEÚDO DO AppLayout.tsx:")
    print("="*60)
    if os.path.exists(caminho_layout):
        with open(caminho_layout, 'r', encoding='utf-8') as f:
            print(f.read())
    else:
        print("❌ AppLayout.tsx não encontrado.")

if __name__ == "__main__":
    diagnosticar()