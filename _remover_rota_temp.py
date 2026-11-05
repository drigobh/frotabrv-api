import os
import re

path = os.path.join(os.getcwd(), "app", "backend", "routers", "auth.py")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Remove o bloco da rota temporária
padrao = r'@router\.post\("/reativar-admin-temporario"\)[\s\S]*?return\s*\{[^}]*\}\n'
c = re.sub(padrao, '', c)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Rota temporária removida do auth.py!")
print("Faça o git push para atualizar o Render.")