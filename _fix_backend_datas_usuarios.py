import os
import re

# 1. Atualizar o auth.py para registrar o último acesso no login
path_auth = os.path.join(os.getcwd(), "app", "backend", "routers", "auth.py")

with open(path_auth, "r", encoding="utf-8") as f:
    a_c = f.read()

# Encontra a função de login e adiciona o update do ultimo_acesso
if "ultimo_acesso" not in a_c:
    # Procura a rota POST /login
    padrao_login = r'@router\.post\("/login"\)[\s\S]*?(?=@router|\Z)'
    match_login = re.search(padrao_login, a_c)
    
    if match_login:
        bloco_login = match_login.group(0)
        # Insere o update do ultimo_acesso logo antes do return (onde o token é gerado)
        novo_bloco = bloco_login.replace(
            "return {",
            'await db.usuarios.update_one({"id": usuario["id"]}, {"$set": {"ultimo_acesso": datetime.now().isoformat()}})\n    return {'
        )
        a_c = a_c.replace(bloco_login, novo_bloco)
        
        # Garantir que o datetime está importado
        if "from datetime import datetime" not in a_c:
            a_c = "from datetime import datetime\n" + a_c
        
        with open(path_auth, "w", encoding="utf-8") as f:
            f.write(a_c)
        print("✅ Backend: Rota de login agora registra o último acesso.")

# 2. Atualizar o usuarios.py para garantir a data_cadastro (ativação)
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
    print("✅ Backend: Campo data_cadastro (ativação) garantido na criação.")

print("\n✅ Backend pronto! Faça o git push.")