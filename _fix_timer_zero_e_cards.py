import os
import re

# ==========================================
# 1. APPLAYOUT: PASSAR O ZERO CORRETAMENTE
# ==========================================
path_layout = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "AppLayout.tsx")

with open(path_layout, "r", encoding="utf-8") as f:
    l_c = f.read()

# Corrigir o operador || que transforma 0 em 30
l_c = l_c.replace(
    'timeoutMinutos={user.timeout_minutos || 30}',
    'timeoutMinutos={user.timeout_minutos !== undefined && user.timeout_minutos !== null ? user.timeout_minutos : 30}'
)

with open(path_layout, "w", encoding="utf-8") as f:
    f.write(l_c)
print("✅ AppLayout: Timer agora aceita o valor 0 (desativado).")

# ==========================================
# 2. PERFIS: FALLBACK NOS CARDS
# ==========================================
path_perfis = os.path.join(os.getcwd(), "frontend", "src", "pages", "Perfis.tsx")

with open(path_perfis, "r", encoding="utf-8") as f:
    p_c = f.read()

# Corrigir a renderização dos cards para usar fallback
p_c = p_c.replace(
    '⏱️ {p.timeout_minutos === 0 ? "Sem timer" : `${p.timeout_minutos} min`}',
    '⏱️ {p.timeout_minutos !== undefined ? (p.timeout_minutos === 0 ? "Sem timer" : `${p.timeout_minutos} min`) : "30 min"}'
)
p_c = p_c.replace(
    '🔒 {p.tentativas_login === "liberado" ? "Liberado" : `${p.tentativas_login} tent.`}',
    '🔒 {p.tentativas_login !== undefined ? (p.tentativas_login === "liberado" ? "Liberado" : `${p.tentativas_login} tent.`) : "5 tent."}'
)

with open(path_perfis, "w", encoding="utf-8") as f:
    f.write(p_c)
print("✅ Perfis: Cards agora têm fallback para valores undefined.")

# ==========================================
# 3. BACKEND: FORÇAR MIGRAÇÃO NOS PERFIS SEM CAMPOS
# ==========================================
path_perfis_back = os.path.join(os.getcwd(), "app", "backend", "routers", "perfis.py")

with open(path_perfis_back, "r", encoding="utf-8") as f:
    b_c = f.read()

# Atualizar a rota de migração para preencher TODOS os perfis
rota_migracao = '''

@router.post("/migrar-seguranca")
async def migrar_seguranca():
    """Força todos os perfis a terem os campos de segurança."""
    perfis = await db.perfis.find({}).to_list(100)
    for p in perfis:
        update = {}
        if "timeout_minutos" not in p or p.get("timeout_minutos") is None:
            update["timeout_minutos"] = 30
        if "tentativas_login" not in p or p.get("tentativas_login") is None:
            update["tentativas_login"] = "5"
        
        if update:
            await db.perfis.update_one({"id": p["id"]}, {"$set": update})
    
    return {"status": "ok", "message": "Perfis migrados com sucesso."}
'''

# Substituir a rota antiga (se existir)
if "migrar-seguranca" in b_c:
    b_c = re.sub(r'@router\.post\("/migrar-seguranca"\)[\s\S]*?(?=@router|\Z)', rota_migracao.strip() + "\n\n", b_c)
else:
    b_c += rota_migracao

with open(path_perfis_back, "w", encoding="utf-8") as f:
    f.write(b_c)
print("✅ Backend: Rota de migração atualizada para preencher todos os perfis.")

print("✅ Tudo pronto! Faça o git push.")