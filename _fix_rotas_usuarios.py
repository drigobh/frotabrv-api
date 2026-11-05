import os
import re

path = os.path.join(os.getcwd(), "app", "backend", "routers", "auth.py")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Descobrir o caminho correto do db
base_dir = os.path.join(os.getcwd(), "app", "backend")
pastas_procura = [
    os.path.join(base_dir, "lib"),
    base_dir,
    os.path.join(base_dir, "database"),
]

import_db = "from lib.db import db"
for pasta in pastas_procura:
    if not os.path.exists(pasta): continue
    for arquivo in os.listdir(pasta):
        if arquivo.endswith(".py"):
            caminho = os.path.join(pasta, arquivo)
            with open(caminho, "r", encoding="utf-8") as f:
                conteudo = f.read()
            if "db = " in conteudo or "db =" in conteudo or "AsyncIOMotorClient" in conteudo:
                import_db = f"from {os.path.basename(pasta)}.{arquivo.replace('.py', '')} import db"
                break
    if import_db != "from lib.db import db": break

# 2. Adicionar o import do db se não existir
if import_db not in c and "import db" not in c:
    c = import_db + "\n" + c
    print(f"✅ Import '{import_db}' adicionado ao auth.py.")

# 3. Adicionar a rota GET /usuarios (listar todos) se não existir
if "@router.get(\"/usuarios\")" not in c:
    rota_listar = '''

@router.get("/usuarios")
async def listar_usuarios(_u: dict = Depends(require("read"))):
    usuarios = await db.usuarios.find({}, {"_id": 0, "senha": 0}).to_list(1000)
    return usuarios
'''
    c += rota_listar
    print("✅ Rota GET /auth/usuarios criada.")

# 4. Garantir que a rota PUT /auth/perfil tenha o import do require correto
# (Já foi corrigido no script anterior, mas vamos verificar)
if "require" not in c.split("router =")[0]:
    print("⚠️ Import do require ainda não está no topo. Verifique manualmente.")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ auth.py corrigido! Rode o git push para atualizar o Render.")