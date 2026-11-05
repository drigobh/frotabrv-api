import os
import re

# 1. Encontrar onde a função require está REALMENTE no projeto
pastas = [
    os.path.join(os.getcwd(), "app", "backend", "lib"),
    os.path.join(os.getcwd(), "app", "backend")
]

arquivo_origem = None
for pasta in pastas:
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
    print(f"✅ Função 'require' encontrada em: {pasta_origem}/{arquivo_origem}.py")
    # Constrói o import relativo correto (ex: from lib.security import require)
    import_correto = f"from {pasta_origem}.{arquivo_origem} import require"
else:
    print("⚠️ Função 'require' não encontrada nos locais padrão. Usando fallback.")
    import_correto = "from lib.security import require"

# 2. Corrigir o arquivo veiculos.py
path = os.path.join(os.getcwd(), "app", "backend", "routers", "veiculos.py")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Remove qualquer import errado que tenha sido adicionado antes
c = re.sub(r'from app\.backend\.lib\.\w+ import require\n', '', c)
c = re.sub(r'from app\.backend\.lib import require\n', '', c)
c = re.sub(r'from \.\.lib\.\w+ import require\n', '', c)
c = re.sub(r'from lib\.\w+ import require\n', '', c)

# Adiciona o import correto logo no topo (após os imports do fastapi)
if import_correto not in c:
    # Encontra a linha do from fastapi
    match_fastapi = re.search(r'(from fastapi import .*?\n)', c)
    if match_fastapi:
        c = c.replace(match_fastapi.group(1), match_fastapi.group(1) + import_correto + "\n")
    else:
        c = import_correto + "\n" + c

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print(f"✅ Import '{import_correto}' injetado no veiculos.py.")