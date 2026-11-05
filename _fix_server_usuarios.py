import os
import re

path_server = os.path.join(os.getcwd(), "app", "backend", "server.py")

with open(path_server, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Encontrar a linha de import dos routers (ex: from routers import pneus, veiculos, ...)
match_import = re.search(r'from routers import ([^\n]+)', c)

if match_import:
    importados = [x.strip() for x in match_import.group(1).split(",")]
    if "usuarios" not in importados:
        importados.append("usuarios")
        novo_import = "from routers import " + ", ".join(importados)
        c = c.replace(match_import.group(0), novo_import)
        print("✅ 'usuarios' adicionado ao import de routers.")
    else:
        print("ℹ️ 'usuarios' já estava no import.")
else:
    # Se não achou, tenta adicionar no topo
    c = "from routers import usuarios\n" + c
    print("⚠️ Import forçado no topo do server.py.")

# 2. Garantir que o include_router está correto
if "include_router(usuarios.router" not in c:
    # Procura o include do auth para colocar logo depois
    match_auth = re.search(r'api_router\.include_router\(auth\.router[^\n]*\n', c)
    if match_auth:
        c = c.replace(match_auth.group(0), match_auth.group(0) + 'api_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])\n')
        print("✅ include_router de usuarios adicionado após auth.")
    else:
        c += '\napi_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])\n'
        print("✅ include_router de usuarios adicionado no final.")

with open(path_server, "w", encoding="utf-8") as f:
    f.write(c)

print("\n✅ server.py corrigido! Faça o git push.")