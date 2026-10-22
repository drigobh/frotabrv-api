import os

def ler_estrutura():
    raiz = os.getcwd()
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Carretas.tsx")
    
    if not os.path.exists(caminho):
        print("❌ Arquivo Carretas.tsx não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    print("🔍 Lendo as partes importantes do arquivo Carretas.tsx...\n")
    
    # Vamos imprimir o trecho do formulário (onde tem os campos) e da tabela
    imprimindo = False
    for i, linha in enumerate(linhas):
        # Encontra o início dos campos (inputs) ou da tabela
        if "Input" in linha or "Label" in linha or "TableHead" in linha:
            imprimindo = True
        
        if imprimindo:
            print(f"{i+1}: {linha.strip()}")
        
        # Para quando encontrar o fim de um bloco (ex: fechamento de div)
        if imprimindo and "</div>" in linha:
            imprimindo = False

if __name__ == "__main__":
    ler_estrutura()