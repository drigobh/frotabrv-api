import os
import re

path = os.path.join(os.getcwd(), "app", "backend", "routers", "auth.py")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Procura a rota /me e substitui
padrao = r'@router\.get\("/me"\)[\s\S]*?(?=@router|\Z)'
nova = '''
@router.get("/me")
async def me(_u: dict = Depends(require("read"))):
    usuario = await db.usuarios.find_one({"id": _u["id"]}, {"_id": 0, "senha": 0})
    if not usuario:
        raise HTTPException(404, "Usuário não encontrado.")
    
    timeout = 30
    if usuario.get("perfil_id"):
        perfil = await db.perfis.find_one({"id": usuario["perfil_id"]}, {"_id": 0})
        if perfil:
            usuario["permissoes"] = perfil.get("permissoes", [])
            usuario["perfil_nome"] = perfil.get("nome", "")
            timeout = perfil.get("timeout_minutos", 30)
    
    usuario["timeout_minutos"] = timeout
    return usuario
'''
if re.search(padrao, c):
    c = re.sub(padrao, nova.strip() + "\n\n", c)
    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("✅ auth.py: rota /me atualizada.")