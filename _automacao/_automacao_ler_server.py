import os

def ler_server():
    raiz = os.getcwd()
    caminho = os.path.join(raiz, "app", "backend", "server.py")
    
    if not os.path.exists(caminho):
        print("❌ Arquivo server.py não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        print("="*50)
        print("📄 CONTEÚDO ATUAL DO server.py:")
        print("="*50)
        print(f.read())
        print("="*50)

if __name__ == "__main__":
    ler_server()