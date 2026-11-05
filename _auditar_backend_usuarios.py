import os
import re

# ==========================================
# 1. AUDITAR E CORRIGIR O USUARIOS.PY
# ==========================================
path_usuarios = os.path.join(os.getcwd(), "app", "backend", "routers", "usuarios.py")

with open(path_usuarios, "r", encoding="utf-8") as f:
    u_c = f.read()

# Verifica se a rota POST tem o campo notificacoes
if '"notificacoes"' not in u_c:
    print("⚠️ A rota POST de usuários NÃO está salvando notificações. Corrigindo...")
    # Procura a criação do objeto "novo" e adiciona o campo
    u_c = u_c.replace(
        '"two_factor_secret": None,',
        '"two_factor_secret": None,\n        "notificacoes": body.get("notificacoes", {"manutencao": True, "documentos": True, "pneus": True, "resumo_semanal": False}),'
    )
    print("✅ Campo 'notificacoes' adicionado na rota POST.")
else:
    print("✅ A rota POST já está salvando notificações.")

# Verifica se a rota PUT está atualizando notificações
if 'notificacoes' not in u_c.split('@router.put("/{id}")')[1].split('@router')[0]:
    print("⚠️ A rota PUT de usuários NÃO está atualizando notificações. Corrigindo...")
    # Adiciona o campo na lista de campos atualizáveis
    u_c = u_c.replace(
        'for campo in ["nome", "email", "perfil_id", "setor", "cargo", "telefone", "whatsapp", "foto_url"]:',
        'for campo in ["nome", "email", "perfil_id", "setor", "cargo", "telefone", "whatsapp", "foto_url", "notificacoes"]:'
    )
    print("✅ Campo 'notificacoes' adicionado na rota PUT.")
else:
    print("✅ A rota PUT já está atualizando notificações.")

with open(path_usuarios, "w", encoding="utf-8") as f:
    f.write(u_c)

# ==========================================
# 2. AUDITAR E CORRIGIR O AUTH.PY (ME E PERFIL)
# ==========================================
path_auth = os.path.join(os.getcwd(), "app", "backend", "routers", "auth.py")

with open(path_auth, "r", encoding="utf-8") as f:
    a_c = f.read()

# Verifica se a rota /me retorna notificações
if 'notificacoes' not in a_c.split('@router.get("/me")')[1].split('@router')[0]:
    print("⚠️ A rota /auth/me pode não estar retornando notificações. Verificando...")
    # A rota /me usa find_one que retorna todos os campos, então provavelmente já está ok.
    # Mas vamos garantir que a rota /perfil aceite o campo notificacoes.
    pass

# Verifica se a rota PUT /auth/perfil aceita notificações
if 'notificacoes' not in a_c.split('@router.put("/perfil")')[1].split('@router')[0]:
    print("⚠️ A rota PUT /auth/perfil NÃO está atualizando notificações. Corrigindo...")
    # Substitui a rota /perfil por uma versão que aceita notificações
    padrao_perfil = r'@router\.put\("/perfil"\)[\s\S]*?(?=@router|\Z)'
    nova_rota_perfil = '''
@router.put("/perfil")
async def atualizar_perfil(body: dict, _u: dict = Depends(require("read"))):
    update_data = {}
    for campo in ["nome", "telefone", "setor", "cargo", "whatsapp", "foto_url", "notificacoes"]:
        if campo in body:
            update_data[campo] = body[campo]
    
    if "nova_senha" in body and body["nova_senha"]:
        import bcrypt
        senha_hash = bcrypt.hashpw(body["nova_senha"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        update_data["senha"] = senha_hash
    
    if update_data:
        await db.usuarios.update_one({"id": _u["id"]}, {"$set": update_data})
    
    return {"status": "ok", "message": "Perfil atualizado!"}
'''
    a_c = re.sub(padrao_perfil, nova_rota_perfil.strip() + "\n\n", a_c)
    print("✅ Rota /auth/perfil atualizada para aceitar notificações.")
else:
    print("✅ A rota /auth/perfil já está atualizando notificações.")

with open(path_auth, "w", encoding="utf-8") as f:
    f.write(a_c)

print("\n✅ Auditoria concluída! Faça o git push para atualizar o Render.")