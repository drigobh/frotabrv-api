import os

def verificar(raiz):
    caminho = os.path.join(raiz, "app", "backend", "server.py")
    if not os.path.exists(caminho):
        print("❌ server.py não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    print("=== LINHAS COM 'abastecimentos' NO SERVER.PY ===\n")
    for i, linha in enumerate(conteudo.split('\n'), 1):
        if 'abastecimentos' in linha:
            print(f"Linha {i}: {linha.strip()}")
    
    print("\n=== FIM ===")

if __name__ == "__main__":
    verificar(os.getcwd())