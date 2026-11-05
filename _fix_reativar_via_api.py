import os
import re

# 1. Caminho do arquivo auth.py
path_auth = os.path.join(os.getcwd(), "app", "backend", "routers", "auth.py")

if not os.path.exists(path_auth):
    print("❌ Arquivo auth.py não encontrado.")
else:
    with open(path_auth, "r", encoding="utf-8") as f:
        c = f.read()

    # 2. Verifica se a rota temporária já existe
    if "reativar-admin-temporario" not in c:
        rota_temp = '''

@router.post("/reativar-admin-temporario")
async def reativar_admin_temporario():
    """Rota temporária para reativar o admin. Remover depois."""
    resultado = await db.usuarios.update_one(
        {"email": "admin@frotabrv.com"},
        {"$set": {"ativo": True}}
    )
    return {"status": "ok", "modificado": resultado.modified_count > 0}
'''
        c += rota_temp
        with open(path_auth, "w", encoding="utf-8") as f:
            f.write(c)
        print("✅ Rota temporária /auth/reativar-admin-temporario criada com sucesso!")
    else:
        print("ℹ️ A rota temporária já existia no arquivo.")

    print("\n🚀 Próximo passo: rodar no terminal:")
    print("   git add .")
    print('   git commit -m "temp: rota para reativar admin"')
    print("   git push")
    print("\nDepois que o Render atualizar, rode o script _reativar_render.py.")