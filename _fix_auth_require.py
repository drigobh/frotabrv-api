import os
import re

# 1. Encontrar onde a função require está REALMENTE no projeto
base_dir = os.path.join(os.getcwd(), "app", "backend")
pastas_procura = [
    os.path.join(base_dir, "lib"),
    base_dir,
    os.path.join(base_dir, "database"),
    os.path.join(base_dir, "core"),
]

arquivo_origem = None
pasta_origem = None
for pasta in pastas_procura:
    if not os.path.exists(pasta): continue
    for arquivo in os.listdir(pasta):
        if arquivo.endswith(".py"):
            caminho = os.path.join(pasta, arquivo)
            with open(caminho, "r", encoding="utf-8") as f:
                conteudo = f.read()
            if "def require" in conteudo:
                arquivo_origem = arquivo.replace(".py", "")
                pasta_origem = os.path.basename(pasta)
                break
    if arquivo_origem:
        break

if arquivo_origem:
    import_correto = f"from {pasta_origem}.{arquivo_origem} import require"
    print(f"✅ Função require encontrada em: {pasta_origem}/{arquivo_origem}.py")
else:
    import_correto = "from lib.security import require"
    print("⚠️ Usando fallback para require: lib.security")

# 2. Corrigir o arquivo auth.py
path_auth = os.path.join(os.getcwd(), "app", "backend", "routers", "auth.py")

with open(path_auth, "r", encoding="utf-8") as f:
    c = f.read()

# Remove imports antigos que possam estar errados
c = re.sub(r'from app\.backend\.lib\.\w+ import require\n', '', c)
c = re.sub(r'from app\.backend\.lib import require\n', '', c)
c = re.sub(r'from \.\.lib\.\w+ import require\n', '', c)
c = re.sub(r'from lib\.\w+ import require\n', '', c)

# Adiciona o import correto se não existir
if import_correto not in c:
    # Procura a linha do from fastapi
    match_fastapi = re.search(r'(from fastapi import .*?\n)', c)
    if match_fastapi:
        c = c.replace(match_fastapi.group(1), match_fastapi.group(1) + import_correto + "\n")
    else:
        c = import_correto + "\n" + c
    print(f"✅ Import '{import_correto}' injetado no auth.py.")

with open(path_auth, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ auth.py corrigido! O Render vai conseguir compilar.")