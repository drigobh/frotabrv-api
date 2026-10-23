import os

def diag(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    print("Procurando a rota /importar...\n")
    for i, linha in enumerate(linhas):
        if '/importar' in linha:
            print(f"Linha {i+1}: {linha.strip()}")
            # Mostra as 3 linhas seguintes
            for j in range(i+1, min(i+4, len(linhas))):
                print(f"  {j+1}: {linhas[j].strip()}")
            print()

if __name__ == "__main__":
    diag(os.getcwd())