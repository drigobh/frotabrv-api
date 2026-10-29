import os

def diagnosticar():
    raiz = os.getcwd()
    resultado = []
    
    # Locais possíveis do arquivo principal do FastAPI
    possiveis = [
        "app/backend/server.py",
        "app/backend/main.py",
        "app/backend/app.py",
        "app/main.py",
        "main.py",
        "server.py",
    ]
    
    encontrado = None
    for p in possiveis:
        caminho = os.path.join(raiz, p)
        if os.path.exists(caminho):
            encontrado = caminho
            break
    
    if encontrado:
        resultado.append(f"=== ARQUIVO PRINCIPAL ENCONTRADO: {encontrado} ===\n")
        with open(encontrado, 'r', encoding='utf-8') as f:
            c = f.read()
        resultado.append(c)
    else:
        resultado.append("❌ Nenhum arquivo principal do FastAPI encontrado nos caminhos comuns.")
        # Varrer a pasta app/backend
        backend = os.path.join(raiz, "app", "backend")
        if os.path.exists(backend):
            resultado.append(f"\nArquivos na pasta app/backend: {os.listdir(backend)}")
    
    with open('debug_server.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(resultado))
    print("✅ Diagnóstico salvo em debug_server.txt")

if __name__ == "__main__":
    diagnosticar()