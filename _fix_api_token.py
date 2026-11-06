import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "lib", "api.ts")

if not os.path.exists(path):
    print("❌ api.ts não encontrado.")
else:
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    # 1. Verificar se o token está sendo lido do localStorage
    if "localStorage.getItem" not in c:
        print("⚠️ O api.ts não está lendo o token do localStorage.")
    else:
        print("✅ O api.ts lê o token do localStorage.")

    # 2. Verificar se o header Authorization está sendo montado
    if "Authorization" not in c:
        print("⚠️ O api.ts não está montando o header Authorization. Corrigindo...")
        # Adiciona um interceptor simples (se o api.ts usar fetch)
        # Vamos apenas garantir que o header seja adicionado no ponto de envio
        c = c.replace(
            'headers: {',
            'headers: {\n      "Authorization": `Bearer ${localStorage.getItem("token") || localStorage.getItem("access_token") || ""}`,'
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(c)
        print("✅ Header Authorization adicionado ao api.ts.")
    else:
        print("✅ O api.ts já monta o header Authorization.")

    # 3. Exibir o conteúdo do api.ts para conferência
    print("\n📄 Conteúdo do api.ts (primeiras 30 linhas):")
    for i, linha in enumerate(c.split("\n")[:30]):
        print(f"{i+1}: {linha}")