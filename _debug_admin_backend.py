import os

# Procura a rota de limpar-base em todos os arquivos .py do backend
pastas = ["app/backend/routers", "app/backend"]
for pasta in pastas:
    caminho_pasta = os.path.join(os.getcwd(), pasta)
    if not os.path.exists(caminho_pasta): continue
    for file in os.listdir(caminho_pasta):
        if file.endswith(".py"):
            caminho = os.path.join(caminho_pasta, file)
            with open(caminho, 'r', encoding='utf-8') as f:
                c = f.read()
            if 'limpar-base' in c or 'limpar_base' in c:
                with open('debug_admin.txt', 'w', encoding='utf-8') as out:
                    out.write(f"--- {caminho} ---\n")
                    # Pega um trecho em volta da rota
                    idx = c.find('limpar')
                    inicio = max(0, idx - 500)
                    fim = min(len(c), idx + 2000)
                    out.write(c[inicio:fim])
                print(f"✅ Trecho extraído de {caminho}. Abra debug_admin.txt")
                exit()

print("❌ Rota de limpeza não encontrada.")