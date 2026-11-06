import os
import re

# ==========================================
# 1. BACKEND: RETORNAR timeout_minutos NO /auth/me
# ==========================================
path_auth = os.path.join(os.getcwd(), "app", "backend", "routers", "auth.py")

with open(path_auth, "r", encoding="utf-8") as f:
    a_c = f.read()

# Procura a rota /me e adiciona o timeout_minutos do perfil
nova_rota_me = '''
@router.get("/me")
async def me(_u: dict = Depends(require("read"))):
    usuario = await db.usuarios.find_one({"id": _u["id"]}, {"_id": 0, "senha": 0})
    if not usuario:
        raise HTTPException(404, "Usuário não encontrado.")
    
    # Busca o timeout do perfil
    timeout = 30  # valor padrão
    if usuario.get("perfil_id"):
        perfil = await db.perfis.find_one({"id": usuario["perfil_id"]}, {"_id": 0})
        if perfil:
            usuario["permissoes"] = perfil.get("permissoes", [])
            usuario["perfil_nome"] = perfil.get("nome", "")
            timeout = perfil.get("timeout_minutos", 30)
    
    usuario["timeout_minutos"] = timeout
    return usuario
'''

padrao_me = r'@router\.get\("/me"\)[\s\S]*?(?=@router|\Z)'
if re.search(padrao_me, a_c):
    a_c = re.sub(padrao_me, nova_rota_me.strip() + "\n\n", a_c)
    print("✅ Backend: Rota /auth/me agora retorna timeout_minutos do perfil.")

with open(path_auth, "w", encoding="utf-8") as f:
    f.write(a_c)

# ==========================================
# 2. FRONTEND: APPLAYOUT PASSA O TIMEOUT PARA O TIMER
# ==========================================
path_layout = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "AppLayout.tsx")

with open(path_layout, "r", encoding="utf-8") as f:
    l_c = f.read()

# Substituir o valor fixo 30 pelo timeout do usuário
l_c = l_c.replace(
    '<SessionTimer timeoutMinutos={30} onTimeout={realizarLogoff} />',
    '<SessionTimer timeoutMinutos={user.timeout_minutos || 30} onTimeout={realizarLogoff} />'
)

with open(path_layout, "w", encoding="utf-8") as f:
    f.write(l_c)
print("✅ Frontend: AppLayout usa o timeout_minutos do perfil no Timer.")

print("✅ Tudo pronto! Faça o git push.")