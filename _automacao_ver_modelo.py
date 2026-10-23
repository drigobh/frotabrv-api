import os

def ver(raiz):
    caminho = os.path.join(raiz, "app", "backend", "models", "abastecimentos.py")
    if not os.path.exists(caminho):
        print("❌ models/abastecimentos.py não encontrado.")
        return
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    print(conteudo)

if __name__ == "__main__":
    ver(os.getcwd())