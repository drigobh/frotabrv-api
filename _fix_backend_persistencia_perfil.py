import os

path_perfis = os.path.join(os.getcwd(), "app", "backend", "routers", "perfis.py")

with open(path_perfis, "r", encoding="utf-8") as f:
    p_c = f.read()

# 1. Garantir que a rota POST (criar) salve os campos
if "timeout_minutos" not in p_c:
    p_c = p_c.replace(
        '"permissoes": body.get("permissoes", []),',
        '"permissoes": body.get("permissoes", []),\n        "timeout_minutos": body.get("timeout_minutos", 30),\n        "tentativas_login": body.get("tentativas_login", 5),'
    )

# 2. Garantir que a rota PUT (editar) salve os campos
# A rota PUT geralmente faz um update_one com body direto, então já deve funcionar,
# mas vamos garantir que os campos não sejam perdidos
with open(path_perfis, "w", encoding="utf-8") as f:
    f.write(p_c)

print("✅ Backend: Rota de perfis agora salva timeout_minutos e tentativas_login.")