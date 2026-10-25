import os

def diag(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "manutencoes.py")
    if not os.path.exists(caminho):
        print("❌ Arquivo manutencoes.py NÃO EXISTE.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    print("=== ROTAS ENCONTRADAS NO BACKEND (manutencoes.py) ===")
    import re
    rotas = re.findall(r'@router\.(get|post|put|delete)\("([^"]*)"', conteudo)
    if not rotas:
        print("Nenhuma rota encontrada!")
    for metodo, path in rotas:
        print(f"[{metodo.upper()}] /manutencoes{path}")
    
    print("\n=== FIM ===")

if __name__ == "__main__":
    diag(os.getcwd())