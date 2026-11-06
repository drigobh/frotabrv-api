import os
import re

# ==========================================
# 1. ATUALIZAR O MODELO DE PERFIS (timeout_minutos, tentativas_login)
# ==========================================
path_perfis = os.path.join(os.getcwd(), "app", "backend", "routers", "perfis.py")

with open(path_perfis, "r", encoding="utf-8") as f:
    p_c = f.read()

# Adiciona os novos campos na criação e atualização de perfis
p_c = p_c.replace(
    '"permissoes": body.get("permissoes", []),',
    '"permissoes": body.get("permissoes", []),\n        "timeout_minutos": body.get("timeout_minutos", 30),\n        "tentativas_login": body.get("tentativas_login", 5),'
)

with open(path_perfis, "w", encoding="utf-8") as f:
    f.write(p_c)
print("✅ Perfis: Campos de timeout e tentativas adicionados.")

# ==========================================
# 2. ATUALIZAR O AUTH.PY (Login com bloqueio, logoff e timeout)
# ==========================================
path_auth = os.path.join(os.getcwd(), "app", "backend", "routers", "auth.py")

with open(path_auth, "r", encoding="utf-8") as f:
    a_c = f.read()

# 2.1. Rota de Login com Contagem de Tentativas e Retorno do Timeout do Perfil
rota_login = '''
@router.post("/login")
async def login(body: dict):
    from datetime import datetime
    usuario = await db.usuarios.find_one({"email": body.get("email")})
    if not usuario:
        raise HTTPException(401, "Credenciais inválidas.")
    
    if not usuario.get("ativo", True):
        raise HTTPException(403, "Usuário inativo.")
    
    # Busca as regras do perfil
    perfil = await db.perfis.find_one({"id": usuario.get("perfil_id")})
    tentativas_permitidas = perfil.get("tentativas_login", 5) if perfil else 5
    timeout_minutos = perfil.get("timeout_minutos", 30) if perfil else 30

    # Verifica bloqueio
    if tentativas_permitidas != "liberado":
        if usuario.get("login_tentativas", 0) >= int(tentativas_permitidas):
            raise HTTPException(403, f"Usuário bloqueado por excesso de tentativas. Contate o administrador.")

    import bcrypt
    if not bcrypt.checkpw(body.get("senha", "").encode('utf-8'), usuario["senha"].encode('utf-8')):
        # Incrementa tentativas
        await db.usuarios.update_one({"id": usuario["id"]}, {"$inc": {"login_tentativas": 1}})
        raise HTTPException(401, "Senha incorreta.")
    
    # Reset tentativas e atualiza último acesso
    await db.usuarios.update_one(
        {"id": usuario["id"]}, 
        {"$set": {"login_tentativas": 0, "ultimo_acesso": datetime.now().isoformat()}}
    )
    
    # Gera o token
    import jwt
    token = jwt.encode({"id": usuario["id"], "email": usuario["email"]}, os.getenv("JWT_SECRET", "secret"), algorithm="HS256")
    
    return {
        "token": token, 
        "usuario": {"id": usuario["id"], "nome": usuario["nome"], "perfil_id": usuario.get("perfil_id")},
        "timeout_minutos": timeout_minutos
    }
'''

# Substitui a rota de login antiga
padrao_login = r'@router\.post\("/login"\)[\s\S]*?(?=@router|\Z)'
a_c = re.sub(padrao_login, rota_login.strip() + "\n\n", a_c)

# 2.2. Rota de Logoff (Registra no banco)
rota_logoff = '''
@router.post("/logoff")
async def logoff(_u: dict = Depends(require("read"))):
    from datetime import datetime
    await db.usuarios.update_one({"id": _u["id"]}, {"$set": {"ultimo_logoff": datetime.now().isoformat()}})
    return {"status": "ok"}
'''
if "logoff" not in a_c:
    a_c += rota_logoff

# Garantir import do os
if "import os" not in a_c:
    a_c = "import os\n" + a_c

with open(path_auth, "w", encoding="utf-8") as f:
    f.write(a_c)
print("✅ Auth: Login com bloqueio, logoff e timeout implementados.")

# ==========================================
# 3. ATUALIZAR USUARIOS.PY (Destravar Usuário)
# ==========================================
path_usuarios = os.path.join(os.getcwd(), "app", "backend", "routers", "usuarios.py")

with open(path_usuarios, "r", encoding="utf-8") as f:
    u_c = f.read()

# Adiciona a rota de destravar
rota_destravar = '''
@router.patch("/{id}/destravar")
async def destravar_usuario(id: str, _u: dict = Depends(require("write"))):
    await db.usuarios.update_one({"id": id}, {"$set": {"login_tentativas": 0}})
    return {"status": "ok", "message": "Usuário destravado."}
'''
if "destravar" not in u_c:
    u_c += rota_destravar

with open(path_usuarios, "w", encoding="utf-8") as f:
    f.write(u_c)
print("✅ Usuarios: Rota para destravar usuário criada.")