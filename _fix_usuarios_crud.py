import os
import re

path = os.path.join(os.getcwd(), "app", "backend", "routers", "usuarios.py")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Garantir que o require está importado no topo
if "import require" not in c.split("router =")[0]:
    # Descobre o caminho correto do require
    base_dir = os.path.join(os.getcwd(), "app", "backend")
    pastas_procura = [
        os.path.join(base_dir, "lib"),
        base_dir,
        os.path.join(base_dir, "core"),
    ]
    import_correto = "from lib.security import require"
    for pasta in pastas_procura:
        if not os.path.exists(pasta): continue
        for arquivo in os.listdir(pasta):
            if arquivo.endswith(".py"):
                caminho = os.path.join(pasta, arquivo)
                with open(caminho, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                if "def require" in conteudo:
                    import_correto = f"from {os.path.basename(pasta)}.{arquivo.replace('.py', '')} import require"
                    break
        if import_correto != "from lib.security import require": break

    # Adiciona o import após a linha do APIRouter
    match_router = re.search(r'(router = APIRouter\(\)\n)', c)
    if match_router:
        c = c.replace(match_router.group(1), match_router.group(1) + import_correto + "\n")
    else:
        c = import_correto + "\n" + c
    print(f"✅ Import '{import_correto}' injetado no usuarios.py.")
else:
    print("ℹ️ Import do require já estava presente.")

# 2. Garantir que o bcrypt está importado (usado no POST)
if "import bcrypt" not in c:
    c = "import bcrypt\n" + c
    print("✅ Import do bcrypt adicionado.")

# 3. Garantir que o uuid está importado (usado no POST)
if "import uuid" not in c:
    c = "import uuid\n" + c
    print("✅ Import do uuid adicionado.")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("\n✅ usuarios.py corrigido! Faça o git push para o Render atualizar.")