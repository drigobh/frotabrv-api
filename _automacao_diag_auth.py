import os

def diagnosticar_auth():
    caminho = os.path.join(os.getcwd(), "app", "backend", "routers", "auth.py")
    
    if not os.path.exists(caminho):
        print("❌ Arquivo auth.py não encontrado.")
        return

    print("=" * 60)
    print("CONTEÚDO DO ROUTER AUTH (foco no login)")
    print("=" * 60)
    
    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    
    # Procura a função de login
    inicio = -1
    for i, linha in enumerate(linhas):
        if "async def login" in linha or "def login" in linha:
            inicio = i
            break
    
    if inicio == -1:
        print("❌ Função de login não encontrada no auth.py.")
        return
    
    # Mostra a função até o final
    for i in range(inicio, len(linhas)):
        print(f"{i+1:03d} | {linhas[i].rstrip()}")
        
        # Para quando encontrar um novo @router (indica o fim da função)
        if i > inicio and "@router" in linhas[i]:
            break

    print("=" * 60)

if __name__ == "__main__":
    diagnosticar_auth()