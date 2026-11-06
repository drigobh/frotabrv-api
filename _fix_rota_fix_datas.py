import os
import re

path = os.path.join(os.getcwd(), "app", "backend", "routers", "usuarios.py")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Remove a exigência de autenticação da rota de correção
c = c.replace(
    'async def fix_datas_cadastro(_u: dict = Depends(require("write"))):',
    'async def fix_datas_cadastro():'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Rota de correção agora está pública (sem autenticação).")