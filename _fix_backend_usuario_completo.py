import os
import re

path = os.path.join(os.getcwd(), "app", "backend", "routers", "usuarios.py")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Atualizar a rota POST (criar usuário) para aceitar todos os campos
nova_rota_post = '''
@router.post("")
async def criar_usuario(body: dict, _u: dict = Depends(require("write"))):
    import bcrypt
    import uuid
    from datetime import datetime
    
    senha_hash = bcrypt.hashpw(body.get("senha", "").encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    novo = {
        "id": str(uuid.uuid4()),
        "nome": body.get("nome"),
        "email": body.get("email"),
        "perfil_id": body.get("perfil_id"),
        "setor": body.get("setor", ""),
        "cargo": body.get("cargo", ""),
        "telefone": body.get("telefone", ""),
        "whatsapp": body.get("whatsapp", ""),
        "foto_url": body.get("foto_url", ""),
        "senha": senha_hash,
        "ativo": True,
        "data_cadastro": datetime.now().isoformat(),
        "ultimo_acesso": None,
        "two_factor_enabled": False,
        "two_factor_secret": None,
    }
    await db.usuarios.insert_one(novo)
    novo.pop("_id", None)
    novo.pop("senha", None)
    return novo
'''

# 2. Atualizar a rota PUT (editar usuário)
nova_rota_put = '''
@router.put("/{id}")
async def atualizar_usuario(id: str, body: dict, _u: dict = Depends(require("write"))):
    update = {}
    for campo in ["nome", "email", "perfil_id", "setor", "cargo", "telefone", "whatsapp", "foto_url"]:
        if campo in body:
            update[campo] = body[campo]
    
    if update:
        await db.usuarios.update_one({"id": id}, {"$set": update})
    return {"status": "ok"}
'''

# 3. Adicionar rota para alterar senha e ativar 2FA
rota_senha_2fa = '''
@router.patch("/{id}/senha")
async def alterar_senha(id: str, body: dict, _u: dict = Depends(require("write"))):
    import bcrypt
    nova_senha = body.get("nova_senha", "")
    if len(nova_senha) < 6:
        raise HTTPException(400, "Senha muito curta.")
    senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    await db.usuarios.update_one({"id": id}, {"$set": {"senha": senha_hash}})
    return {"status": "ok", "message": "Senha atualizada."}

@router.patch("/{id}/2fa")
async def alternar_2fa(id: str, body: dict, _u: dict = Depends(require("write"))):
    ativo = body.get("ativo", False)
    await db.usuarios.update_one({"id": id}, {"$set": {"two_factor_enabled": ativo}})
    return {"status": "ok", "two_factor_enabled": ativo}
'''

# Substituir as rotas antigas
padrao_post = r'@router\.post\(""\)[\s\S]*?(?=@router|$)'
padrao_put = r'@router\.put\("/\{id\}"\)[\s\S]*?(?=@router|$)'

c = re.sub(padrao_post, nova_rota_post.strip() + "\n\n", c)
c = re.sub(padrao_put, nova_rota_put.strip() + "\n\n", c)

# Adicionar as novas rotas se não existirem
if "alterar_senha" not in c:
    c += "\n" + rota_senha_2fa

# Garantir imports
if "import bcrypt" not in c:
    c = "import bcrypt\n" + c
if "import uuid" not in c:
    c = "import uuid\n" + c
if "from datetime import datetime" not in c:
    c = "from datetime import datetime\n" + c
if "from fastapi import HTTPException" not in c:
    c = "from fastapi import HTTPException\n" + c

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Backend: Rotas de usuário completas (foto, setor, cargo, senha, 2FA).")