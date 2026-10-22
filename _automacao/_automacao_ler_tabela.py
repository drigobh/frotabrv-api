import os

def ler_tabela():
    raiz = os.getcwd()
    caminho = os.path.join(raiz, "frontend", "src", "components", "cadastros", "CadastroTable.tsx")
    
    if not os.path.exists(caminho):
        print("❌ Arquivo CadastroTable.tsx não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    print("🔍 Lendo as primeiras 50 linhas do CadastroTable.tsx...\n")
    
    linhas = conteudo.splitlines()
    for i, linha in enumerate(linhas[:50]):
        print(f"{i+1}: {linha}")

if __name__ == "__main__":
    ler_tabela()