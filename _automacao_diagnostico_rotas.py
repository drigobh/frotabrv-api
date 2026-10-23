import os

def diagnosticar(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    
    if not os.path.exists(caminho):
        print("❌ Arquivo abastecimentos.py não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    print(f"📄 Analisando {caminho}...\n")
    print("Buscando rotas (linhas que começam com @router):\n")
    
    for i, linha in enumerate(linhas):
        if '@router' in linha:
            print(f"  Linha {i+1}: {linha.strip()}")

if __name__ == "__main__":
    diagnosticar(os.getcwd())