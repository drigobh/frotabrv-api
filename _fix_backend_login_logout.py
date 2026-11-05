import os
import re

# ==========================================
# 1. CORRIGIR O LOGIN (Registrar Último Acesso)
# ==========================================
path_auth = os.path.join(os.getcwd(), "app", "backend", "routers", "auth.py")

with open(path_auth, "r", encoding="utf-8") as f:
    a_c = f.read()

# Garantir que o datetime está importado
if "from datetime import datetime" not in a_c:
    a_c = "from datetime import datetime\n" + a_c

# Procura a rota POST /login
padrao_login = r'@router\.post\("/login"\)[\s\S]*?(?=@router|\Z)'
match_login = re.search(padrao_login, a_c)

if match_login:
    bloco = match_login.group(0)
    # Verifica se já tem o update do ultimo_acesso
    if "ultimo_acesso" not in bloco:
        # Insere antes do return
        novo_bloco = bloco.replace(
            "return {",
            'await db.usuarios.update_one({"id": usuario["id"]}, {"$set": {"ultimo_acesso": datetime.now().isoformat()}})\n    return {'
        )
        a_c = a_c.replace(bloco, novo_bloco)
        print("✅ Backend: Login agora registra o último acesso.")

with open(path_auth, "w", encoding="utf-8") as f:
    f.write(a_c)

# ==========================================
# 2. GARANTIR QUE O USUARIO NÃO SEJA CRIADO SEM DATA_CADASTRO
# ==========================================
path_usuarios = os.path.join(os.getcwd(), "app", "backend", "routers", "usuarios.py")

with open(path_usuarios, "r", encoding="utf-8") as f:
    u_c = f.read()

if "data_cadastro" not in u_c:
    u_c = u_c.replace(
        '"ultimo_acesso": None,',
        '"data_cadastro": datetime.now().isoformat(),\n        "ultimo_acesso": None,'
    )
    if "from datetime import datetime" not in u_c:
        u_c = "from datetime import datetime\n" + u_c
    with open(path_usuarios, "w", encoding="utf-8") as f:
        f.write(u_c)
    print("✅ Backend: Campo data_cadastro garantido na criação.")

print("✅ Backend corrigido! Faça o git push.")