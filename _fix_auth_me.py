import os
import re

path = os.path.join(os.getcwd(), "app", "backend", "routers", "auth.py")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Procura a função "me" (ou "get_me") e substitui para retornar todos os campos
padrao = r'@router\.get\("/me"\)[\s\S]*?(?=@router|\Z)'

nova_rota_me = '''
@router.get("/me")
async def me(_u: dict = Depends(require("read"))):
    usuario = await db.usuarios.find_one({"id": _u["id"]}, {"_id": 0, "senha": 0})
    if not usuario:
        raise HTTPException(404, "Usuário não encontrado.")
    return usuario
'''

if re.search(padrao, c):
    c = re.sub(padrao, nova_rota_me.strip() + "\n\n", c)
    print("✅ Backend: Rota /auth/me atualizada para retornar todos os campos.")
else:
    print("⚠️ Rota /auth/me não encontrada. Verifique o arquivo auth.py.")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)