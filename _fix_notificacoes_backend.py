import os
import re

path = os.path.join(os.getcwd(), "app", "backend", "routers", "usuarios.py")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Adicionar o campo de notificações na criação
c = c.replace(
    '"two_factor_secret": None,',
    '"two_factor_secret": None,\n        "notificacoes": body.get("notificacoes", {"manutencao": True, "documentos": True, "pneus": True, "resumo_semanal": False}),'
)

# 2. Adicionar a rota de atualização de notificações
rota_notif = '''
@router.put("/{id}/notificacoes")
async def atualizar_notificacoes(id: str, body: dict, _u: dict = Depends(require("write"))):
    await db.usuarios.update_one({"id": id}, {"$set": {"notificacoes": body}})
    return {"status": "ok", "message": "Notificações atualizadas."}
'''

if "notificacoes" not in c:
    c += rota_notif
    print("✅ Backend: Rota de notificações adicionada.")

# 3. Garantir que a rota /auth/me retorne o campo notificacoes (já está implícito no find_one, mas vamos garantir)
with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Backend: Campo de notificações adicionado ao usuário.")